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
        Tests strength levels (2.0 to 8.0) in parallel using batching.
        Stops before the model starts looping (Repetition Check).
        """
        # Renamed from auto_tune_strength to auto_tune to match gca_agent_final.py
        print(f"[🔧] Auto-Tuning Strength...")
        candidates = [2.0, 4.0, 6.0, 8.0]
        batch_size = len(candidates)
        best_strength = 2.0

        inputs = self.gb.tokenizer(prompt, return_tensors="pt").to(DEVICE)
        skill_vec = skill_vec.to(DEVICE)

        # Batch inputs
        # Repeat input_ids and attention_mask for each candidate strength
        input_ids = inputs["input_ids"].repeat(batch_size, 1)
        attention_mask = inputs["attention_mask"].repeat(batch_size, 1)

        # Prepare steering tensor for batch injection
        # strengths: (batch_size, 1, 1)
        strengths = torch.tensor(candidates, device=DEVICE, dtype=skill_vec.dtype).view(batch_size, 1, 1)
        # skill_vec: (hidden_size) -> (1, 1, hidden_size)
        skill_vec_reshaped = skill_vec.view(1, 1, -1)
        # steering_tensor: (batch_size, 1, hidden_size) - ready for broadcasting over seq_len
        steering_tensor = strengths * skill_vec_reshaped

        # Inject
        def steer_hook(module, input, output):
            # output[0] shape: (batch_size, seq_len, hidden_size)
            # Use in-place addition on the tensor reference to avoid tuple assignment error
            output[0].add_(steering_tensor)
            return output

        handle = self.gb.model.transformer.h[self.layer_idx].register_forward_hook(steer_hook)

        # Fast generation probe (20 tokens) - Batched
        try:
            out = self.gb.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=20,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.gb.tokenizer.eos_token_id
            )
        finally:
            handle.remove()

        # Evaluate candidates sequentially
        for i, strength in enumerate(candidates):
            text = self.gb.tokenizer.decode(out[i], skip_special_tokens=True)

            # Simple Repetition Check (compression ratio)
            # If "a b a b a b", ratio is high.
            tokens = text.split()
            unique_tokens = len(set(tokens))
            total_tokens = len(tokens)
            ratio = unique_tokens / (total_tokens + 1e-5)

            print(f"    -> Str {strength}: Diversity Ratio {ratio:.2f}")

            if ratio < 0.6: # Looping detected!
                print(f"       ⚠️ Looping detected. Backing off.")
                break # Stop, use previous strength

            best_strength = strength

        print(f"    -> Optimal Strength: {best_strength}")
        return best_strength
