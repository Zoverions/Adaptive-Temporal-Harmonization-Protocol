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
        # Ensure padding token is set for batching
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)

    def harvest_states(self, prompts, batch_size=8):
        harvested = []
        # Store current batch mask for use in hook
        current_mask = None

        def hook(module, input, output):
            # output[0] shape: (batch_size, seq_len, hidden_dim)
            hidden_states = output[0]

            if current_mask is not None:
                # Use mask to ignore padding tokens
                # mask shape: (batch_size, seq_len)
                mask = current_mask.unsqueeze(-1).to(hidden_states.device) # (batch_size, seq_len, 1)

                masked_hidden_states = hidden_states * mask
                sum_states = torch.sum(masked_hidden_states, dim=1) # (batch_size, hidden_dim)

                lengths = torch.sum(mask, dim=1) # (batch_size, 1)
                # Avoid division by zero
                lengths = torch.clamp(lengths, min=1e-9)

                mean_states = sum_states / lengths
            else:
                # Fallback if no mask (should not happen with batch processing as implemented)
                mean_states = torch.mean(hidden_states, dim=1)

            harvested.append(mean_states.detach())

        handle = self.model.transformer.h[6].register_forward_hook(hook)  # Layer 6

        try:
            for i in range(0, len(prompts), batch_size):
                batch_prompts = prompts[i : i + batch_size]
                # Tokenize batch with padding
                inputs = self.tokenizer(batch_prompts, return_tensors="pt", padding=True, truncation=True).to(DEVICE)

                # Update mask for hook
                current_mask = inputs['attention_mask']

                with torch.no_grad():
                    self.model(**inputs)
        finally:
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
