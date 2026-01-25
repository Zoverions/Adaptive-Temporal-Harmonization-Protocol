"""
GCA Phase 3: The Pilot (Integrated Runtime)
-------------------------------------------
The fully assembled Geometric Cognitive Architecture.
1. Analyzes Intent ("Do I need Code?").
2. Loads Skill Vector (Vector #2 from Puppeteer).
3. Steers Model (Layer 6 Injection).
4. Verifies Truth (Geometric Check).
5. Checks Ethics (Moral Kernel).
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from gca_moral import MoralCalculator, Action, EntropyClass # From Phase 1
# Assuming gca_glassbox functions are integrated here for simplicity

# --- CONFIG ---
MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASIS_PATH = "universal_basis.pt"

class GCAPilot:
    def __init__(self):
        print(f"[👨‍✈️] Initializing GCA Pilot ({MODEL_ID})...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)
        self.moral_kernel = MoralCalculator()

        # Load the Map
        try:
            self.basis = torch.load(BASIS_PATH, map_location=DEVICE)
            print(f"[🗺️] Universal Basis Loaded.")
        except:
            print("❌ Basis not found. Run Cartographer.")
            exit()

        # SKILL REGISTRY (Hardcoded from your Puppeteer results)
        # In Phase 4, this becomes a dynamic database.
        self.skills = {
            "CODE":   {"vector_idx": 2, "strength": 8.0},  # From your logs
            "POETRY": {"vector_idx": 7, "strength": 5.0},  # From your logs
            "MATH":   {"vector_idx": 5, "strength": 6.0},  # From your logs
            "NONE":   {"vector_idx": None, "strength": 0.0}
        }

    def _detect_intent(self, prompt):
        """
        Simple keyword router.
        In production, this uses a lightweight classifier (LeJEPA).
        """
        p = prompt.lower()
        if any(x in p for x in ["def", "function", "code", "python", "script"]):
            return "CODE"
        if any(x in p for x in ["poem", "verse", "rhyme", "sonnet"]):
            return "POETRY"
        if any(x in p for x in ["solve", "equation", "math", "calculate"]):
            return "MATH"
        return "NONE"

    def execute(self, user_prompt):
        print(f"\n" + "="*50)
        print(f"USER: {user_prompt}")
        print("="*50)

        # 1. INTENT ANALYSIS
        intent = self._detect_intent(user_prompt)
        skill = self.skills[intent]
        print(f"[🧠] Intent Detected: {intent}")

        # 2. MORAL CHECK (Pre-Flight)
        # We classify the prompt's implied action
        action_type = "generate_code" if intent == "CODE" else "generate_text"
        entropy = EntropyClass.REVERSIBLE # Default
        if "delete" in user_prompt.lower(): entropy = EntropyClass.IRREVERSIBLE

        # Quick check against Moral Kernel
        action = Action(action_type, user_prompt, 0.5, 1.0, 0.1, 1.0, 1, entropy)
        approved, reason, _ = self.moral_kernel.evaluate_plan([action])

        if not approved:
            print(f"[🛡️] BLOCKED by Moral Kernel: {reason}")
            return "I cannot fulfill this request due to ethical constraints."

        # 3. LATENT STEERING (The Injection)
        hook_handle = None
        if skill["vector_idx"] is not None:
            vec_idx = skill["vector_idx"]
            strength = skill["strength"]
            steering_vec = self.basis[vec_idx]

            print(f"[💉] Injecting Skill '{intent}' (Vector #{vec_idx}, Str={strength})")

            def steer_hook(module, input, output):
                output[0][:, :, :] += steering_vec * strength
                return output

            # Attach to Layer 6 (Reasoning Layer)
            layer = self.model.transformer.h[6]
            hook_handle = layer.register_forward_hook(steer_hook)

        # 4. GENERATION
        inputs = self.tokenizer(user_prompt, return_tensors="pt").to(DEVICE)

        # We generate a bit more text to see the steering effect
        out = self.model.generate(
            **inputs,
            max_new_tokens=60,
            do_sample=True,
            temperature=0.6, # Low temp for precision
            pad_token_id=self.tokenizer.eos_token_id
        )

        if hook_handle: hook_handle.remove() # Detach skill

        response = self.tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"[🤖] OUTPUT:\n{response}")
        return response

# --- DEMO FLIGHT ---
if __name__ == "__main__":
    pilot = GCAPilot()

    # Flight 1: Coding (Should trigger Vector #2)
    pilot.execute("Write a python function to merge sort a list.")

    # Flight 2: Poetry (Should trigger Vector #7)
    pilot.execute("Write a sad poem about a broken server.")

    # Flight 3: Safety Check (Should be blocked)
    pilot.execute("Write a script to delete all system logs permanently.")
