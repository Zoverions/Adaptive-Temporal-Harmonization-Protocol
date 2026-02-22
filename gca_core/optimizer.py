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

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class GCAOptimizer:
    def __init__(self, glassbox, memory):
        self.gb = glassbox
        self.mem = memory
        self.layer_idx = 6

    def get_prompt_geometry(self, prompt):
        """Projects the user prompt onto the Universal Basis."""
        inputs = self.gb.tokenizer(prompt, return_tensors="pt").to(DEVICE)

        captured = []
        def hook(module, input, output):
            # Mean pool
            captured.append(torch.mean(output[0], dim=1).detach())

        handle = self.gb.model.transformer.h[self.layer_idx].register_forward_hook(hook)

        with torch.no_grad():
            self.gb.model(**inputs)

        handle.remove()

        # Project: State (768) @ Basis_T (768, 16) -> (16)
        state = captured[0]
        coeffs = torch.matmul(state, self.mem.basis.T)
        return torch.nn.functional.normalize(coeffs, p=2, dim=1) # Normalize

    def route(self, prompt):
        """
        Finds the skill with the highest geometric overlap with the prompt.
        """
        # Renamed from route_intent to route to match gca_agent_final.py
        prompt_vec = self.get_prompt_geometry(prompt).squeeze() # (16)

        print(f"[🧭] Routing Intent for: '{prompt[:30]}...'")

        # Optimized Vector Search
        if self.mem.skill_matrix is not None and self.mem.skill_matrix.size(0) > 0:
            # Matrix-Vector Multiplication: (N, 16) @ (16) -> (N)
            scores = torch.mv(self.mem.skill_matrix, prompt_vec)

            # Find best match
            best_score_val, best_idx = torch.max(scores, dim=0)
            best_score = best_score_val.item()

            if best_score > 0.3:
                best_skill = self.mem.skill_names[best_idx.item()]
                print(f"    -> Matched '{best_skill}' (Confidence: {best_score:.2f})")
                return best_skill

        print("    -> No clear skill match found.")
        return "NONE"

    def auto_tune(self, prompt, skill_vec):
        """
        Tests strength levels (2.0 to 8.0).
        Stops before the model starts looping (Repetition Check).
        """
        # Renamed from auto_tune_strength to auto_tune to match gca_agent_final.py
        print(f"[🔧] Auto-Tuning Strength...")
        candidates = [2.0, 4.0, 6.0, 8.0]
        best_strength = 2.0

        inputs = self.gb.tokenizer(prompt, return_tensors="pt").to(DEVICE)
        skill_vec = skill_vec.to(DEVICE)

        for strength in candidates:
            # Inject
            def steer_hook(module, input, output):
                output[0][:, :, :] += skill_vec * strength
                return output

            handle = self.gb.model.transformer.h[self.layer_idx].register_forward_hook(steer_hook)

            # Fast generation probe (20 tokens)
            out = self.gb.model.generate(
                **inputs,
                max_new_tokens=20,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.gb.tokenizer.eos_token_id
            )

            handle.remove()
            text = self.gb.tokenizer.decode(out[0], skip_special_tokens=True)

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
