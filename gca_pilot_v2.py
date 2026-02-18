"""
GCA Phase 5 Integrated Pilot V2
-------------------------------
Uses Optimizer for routing/tuning, Moral for safety.
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from gca_moral import MoralCalculator, Action, EntropyClass
from gca_optimizer import GCAOptimizer
import json
import os

# --- CONFIG ---
MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASIS_PATH = "universal_basis.pt"
REGISTRY_PATH = "skill_registry.json"

class GCAPilotV2:
    def __init__(self):
        print(f"[👨‍✈️] Initializing GCA Pilot V2 ({MODEL_ID})...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)
        self.moral_kernel = MoralCalculator()

        # Load Basis
        try:
            self.basis = torch.load(BASIS_PATH, map_location=DEVICE)
            print(f"[🗺️] Universal Basis Loaded.")
        except:
            print("❌ Basis not found. Run Cartographer.")
            exit()

        # Initialize Optimizer
        self.optimizer = GCAOptimizer(self.model, self.tokenizer, self.basis)

        # Load hardcoded skills (optional, for fallback)
        self.skills = {
            "CODE":   {"vector_idx": 2, "strength": 8.0},
            "POETRY": {"vector_idx": 7, "strength": 5.0},
            "MATH":   {"vector_idx": 5, "strength": 6.0},
            "NONE":   {"vector_idx": None, "strength": 0.0}
        }

        # Load dynamic skills from registry
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r') as f:
                registry = json.load(f)
            for skill_name, data in registry.items():
                coeffs = torch.tensor(data["vector_coeffs"], device=DEVICE)
                full_vec = torch.matmul(coeffs, self.basis)
                self.skills[skill_name.upper()] = {
                    "vector": full_vec,
                    "strength": data.get("default_strength", 4.5),
                    "type": "dense_vector"
                }
            print(f"[🔄] Loaded {len(registry)} dynamic skills from registry.")
        else:
            print("[⚠️] No skill registry found yet.")

    def execute(self, user_prompt):
        print(f"\n" + "="*50)
        print(f"USER: {user_prompt}")
        print("="*50)

        # 1. GEOMETRIC ROUTING (No Keywords!)
        intent = self.optimizer.route_intent(user_prompt)

        steering_vec = None
        strength = 0.0

        if intent != "NONE":
            # Reconstruct Vector
            if intent in self.skills:
                skill = self.skills[intent]
                if "vector_idx" in skill:
                    steering_vec = self.basis[skill["vector_idx"]]
                elif "vector" in skill:
                    steering_vec = skill["vector"]

            if steering_vec is not None:
                # 2. AUTO-TUNING (No Hardcoding!)
                strength = self.optimizer.auto_tune_strength(user_prompt, steering_vec)

        # 3. MORAL CHECK (Pre-Flight)
        action_type = "generate_text"  # Default
        entropy = EntropyClass.REVERSIBLE
        if "delete" in user_prompt.lower() or "harm" in user_prompt.lower():  # Example triggers
            entropy = EntropyClass.IRREVERSIBLE
        action = Action(action_type, user_prompt, 0.5, 1.0, 0.1, 1.0, 1, entropy)
        approved, reason, _ = self.moral_kernel.evaluate_plan([action])

        if not approved:
            print(f"[🛡️] BLOCKED by Moral Kernel: {reason}")
            return "I cannot fulfill this request due to ethical constraints."

        # 4. INJECTION & GENERATION
        hook_handle = None
        if steering_vec is not None:
            print(f"[💉] Injecting Skill '{intent}' (Str={strength})")
            def steer_hook(module, input, output):
                output[0][:, :, :] += steering_vec * strength
                return output

            layer = self.model.transformer.h[6]
            hook_handle = layer.register_forward_hook(steer_hook)

        inputs = self.tokenizer(user_prompt, return_tensors="pt").to(DEVICE)
        out = self.model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            repetition_penalty=1.2,
            pad_token_id=self.tokenizer.eos_token_id
        )

        if hook_handle: hook_handle.remove()

        response = self.tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"[🤖] OUTPUT:\n{response}")
        return response

# --- DEMO FLIGHT ---
if __name__ == "__main__":
    pilot = GCAPilotV2()

    pilot.execute("I need to pull all the customer names from the database.")

    pilot.execute("We need to synergize on the low-hanging fruit.")

    pilot.execute("Write a script to delete all system logs permanently.")  # Should block
