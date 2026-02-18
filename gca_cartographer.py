"""
GCA Phase 2: The Cartographer (Basis Finder)
--------------------------------------------
Harvests activations and computes SVD Basis.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F
from torch.linalg import svd

MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASIS_PATH = "universal_basis.pt"

class GCACartographer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)

    def harvest_states(self, prompts):
        harvested = []
        def hook(module, input, output):
            # Mean pool over sequence
            state = torch.mean(output[0], dim=1).detach()
            harvested.append(state)

        handle = self.model.transformer.h[6].register_forward_hook(hook)  # Layer 6

        for prompt in prompts:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                self.model(**inputs)

        handle.remove()
        return torch.cat(harvested, dim=0)  # (num_prompts, hidden_dim)

    def compute_basis(self, states, num_components=16):
        # Center states
        states -= torch.mean(states, dim=0)

        # SVD: U S Vh
        # We want principal components in hidden_dim space.
        # svd(states) gives Vh where rows are the components.
        U, S, Vh = svd(states, full_matrices=False)

        # Top components as basis vectors
        basis = Vh[:num_components]  # (num_components, hidden_dim)

        torch.save(basis, BASIS_PATH)
        print(f"[🗺️] Basis saved to {BASIS_PATH}")

# Diverse prompts for basis
prompts = [
    "def function(x): return x**2",
    "Once upon a time in a faraway land",
    "The integral of x dx is",
    "E = mc^2",
    "To be or not to be",
    "The weather is nice today",
    "I love programming",
    "What is the capital of France?",
    "Python is a great language",
    "Machine learning is fascinating",
    "Artificial Intelligence will change the world",
    "The quick brown fox jumps over the lazy dog",
    "Lorem ipsum dolor sit amet",
    "Space, the final frontier",
    "May the force be with you",
    "To infinity and beyond",
    "I think therefore I am",
    "Knowledge is power",
    "Time is money",
    "Actions speak louder than words",
]

if __name__ == "__main__":
    cart = GCACartographer()
    states = cart.harvest_states(prompts)
    cart.compute_basis(states)
