"""
GCA Phase 4: The School (Dynamic Skill Learner)
-----------------------------------------------
1. Accepts examples of a new skill.
2. Extracts the 'Essence Vector'.
3. Saves it to the Skill Registry.
"""

import torch
import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- CONFIG ---
MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASIS_PATH = "universal_basis.pt"
REGISTRY_PATH = "skill_registry.json"

class GCASchool:
    def __init__(self):
        print(f"[🏫] Initializing GCA School ({MODEL_ID})...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)

        # Load the Map
        try:
            self.basis = torch.load(BASIS_PATH, map_location=DEVICE)
        except:
            print("❌ Basis not found. Run Cartographer.")
            exit()

    def learn_skill(self, name, examples):
        print(f"\n[🎓] Learning Skill: '{name}' from {len(examples)} examples...")

        harvested_states = []
        current_mask = None

        # 1. Harvest Activations
        def harvest_hook(module, input, output):
            # output might be a tuple or a tensor depending on how the model returns it
            if isinstance(output, tuple):
                hidden_states = output[0]
            else:
                hidden_states = output

            if current_mask is not None:
                # Use mask to ignore padding tokens
                # mask shape: (batch_size, seq_len)
                mask = current_mask.unsqueeze(-1).to(hidden_states.device) # (batch_size, seq_len, 1)

                masked_hidden_states = hidden_states * mask
                sum_states = torch.sum(masked_hidden_states, dim=1) # (batch_size, hidden_dim)

                lengths = torch.sum(mask, dim=1).float() # (batch_size, 1)
                # Avoid division by zero
                lengths = torch.clamp(lengths, min=1e-9)

                mean_states = sum_states / lengths
            else:
                # Fallback if no mask
                mean_states = torch.mean(hidden_states, dim=1)

            for i in range(mean_states.size(0)):
                harvested_states.append(mean_states[i].unsqueeze(0).detach())

        layer = self.model.transformer.h[6] # Same layer as Pilot
        handle = layer.register_forward_hook(harvest_hook)

        batch_size = 8
        for i in range(0, len(examples), batch_size):
            batch_ex = examples[i : i + batch_size]
            inputs = self.tokenizer(batch_ex, return_tensors="pt", padding=True, truncation=True).to(DEVICE)

            current_mask = inputs['attention_mask']

            with torch.no_grad():
                self.model(**inputs)

        handle.remove()

        # 2. Compute Essence (Mean Vector)
        # Shape: (num_examples, 768) -> (768)
        raw_mean = torch.mean(torch.cat(harvested_states, dim=0), dim=0)

        # 3. Project onto Universal Basis (Clean the Noise)
        # Coefficients = Vector dot Basis_T
        # (768) dot (768, 16) -> (16)
        coeffs = torch.matmul(raw_mean, self.basis.T)

        # Normalize coefficients for consistent strength
        coeffs = torch.nn.functional.normalize(coeffs, p=2, dim=0)

        print(f"    -> Extracted Signature: {coeffs[:4].tolist()}...")

        # 4. Save to Registry
        self._save_to_registry(name, coeffs.tolist())

    def _save_to_registry(self, name, coeffs):
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r') as f:
                registry = json.load(f)
        else:
            registry = {}

        registry[name] = {
            "vector_coeffs": coeffs,
            "layer": 6,
            "default_strength": 5.0
        }

        with open(REGISTRY_PATH, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"[💾] Skill '{name}' saved to {REGISTRY_PATH}")

# --- TEACHING SESSION ---
if __name__ == "__main__":
    school = GCASchool()

    # Teach it SQL (which GPT-2 is bad at naturally)
    sql_examples = [
        "SELECT * FROM users WHERE age > 18;",
        "INSERT INTO orders (id, item) VALUES (1, 'apple');",
        "SELECT count(*) FROM sales GROUP BY region;",
        "UPDATE employees SET salary = salary * 1.1;",
        "DELETE FROM logs WHERE date < '2023-01-01';"
    ]

    school.learn_skill("SQL", sql_examples)

    # Teach it "Corporate Speak"
    corp_examples = [
        "Let's circle back on this offline.",
        "We need to leverage our core competencies.",
        "This is a value-add for the stakeholders.",
        "Let's drill down into the low-hanging fruit."
    ]

    school.learn_skill("CORPORATE", corp_examples)
