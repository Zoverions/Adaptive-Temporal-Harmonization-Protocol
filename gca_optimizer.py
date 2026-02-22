"""
GCA Phase 5: The Optimizer (Geometric Router & Auto-Tuner)
----------------------------------------------------------
1. Semantic Router: Matches prompt geometry to skill geometry.
2. Auto-Tuner: Finds optimal steering strength by measuring repetition.
"""

import torch
import torch.nn.functional as F
import json
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- CONFIG ---
MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASIS_PATH = "universal_basis.pt"
REGISTRY_PATH = "skill_registry.json"

class GCAOptimizer:
    def __init__(self, model, tokenizer, basis):
        self.model = model
        self.tokenizer = tokenizer
        self.basis = basis
        self.layer_idx = 6

        # Load Registry
        with open(REGISTRY_PATH, 'r') as f:
            self.registry = json.load(f)

    def get_prompt_geometry(self, prompt):
        """Projects the user prompt onto the Universal Basis."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)

        captured = []
        def hook(module, input, output):
            # Mean pool
            captured.append(torch.mean(output[0], dim=1).detach())

        handle = self.model.transformer.h[self.layer_idx].register_forward_hook(hook)

        with torch.no_grad():
            self.model(**inputs)

        handle.remove()

        # Project: State (768) @ Basis_T (768, 16) -> (16)
        state = captured[0]
        coeffs = torch.matmul(state, self.basis.T)
        return torch.nn.functional.normalize(coeffs, p=2, dim=1) # Normalize

    def route_intent(self, prompt):
        """
        Finds the skill with the highest geometric overlap with the prompt.
        """
        prompt_vec = self.get_prompt_geometry(prompt).squeeze() # (16)

        best_skill = "NONE"
        best_score = 0.3 # Minimum confidence threshold

        print(f"[🧭] Routing Intent for: '{prompt[:30]}...'")

        for name, data in self.registry.items():
            skill_coeffs = torch.tensor(data["vector_coeffs"], device=DEVICE)

            # Cosine Similarity
            score = torch.dot(prompt_vec, skill_coeffs).item()

            if score > best_score:
                best_score = score
                best_skill = name

        if best_skill != "NONE":
            print(f"    -> Matched '{best_skill}' (Confidence: {best_score:.2f})")
        else:
            print("    -> No clear skill match found.")

        return best_skill

    def auto_tune_strength(self, prompt, skill_vec):
        """
        Tests strength levels (2.0 to 8.0).
        Stops before the model starts looping (Repetition Check).
        """
        print(f"[🔧] Auto-Tuning Strength...")
        candidates = [2.0, 4.0, 6.0, 8.0]
        best_strength = 2.0

        inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
        skill_vec = skill_vec.to(DEVICE)

        # Batch inputs
        batch_size = len(candidates)
        # Duplicate input_ids and attention_mask
        input_ids = inputs["input_ids"].repeat(batch_size, 1)
        attention_mask = inputs["attention_mask"].repeat(batch_size, 1)

        # Prepare steering tensor
        # candidates -> (batch, 1, 1)
        strength_tensor = torch.tensor(candidates, device=DEVICE).view(batch_size, 1, 1)
        # skill_vec -> (1, 1, hidden)
        skill_vec_view = skill_vec.view(1, 1, -1)
        # steering -> (batch, 1, hidden)
        steering_tensor = skill_vec_view * strength_tensor

        # Inject
        def steer_hook(module, input, output):
            # output[0]: (batch, seq, hidden)
            # steering_tensor broadcasts over seq
            output[0][:, :, :] += steering_tensor
            return output

        handle = self.model.transformer.h[self.layer_idx].register_forward_hook(steer_hook)

        # Fast generation probe (20 tokens)
        try:
            out = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=20,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        finally:
            handle.remove()

        for i, strength in enumerate(candidates):
            text = self.tokenizer.decode(out[i], skip_special_tokens=True)

            # Simple Repetition Check (compression ratio)
            # If "a b a b a b", ratio is high.
            unique_tokens = len(set(text.split()))
            total_tokens = len(text.split())
            ratio = unique_tokens / (total_tokens + 1e-5)

            print(f"    -> Str {strength}: Diversity Ratio {ratio:.2f}")

            if ratio < 0.6: # Looping detected!
                print(f"       ⚠️ Looping detected. Backing off.")
                break # Stop, use previous strength

            best_strength = strength

        print(f"    -> Optimal Strength: {best_strength}")
        return best_strength
