import torch
import json
import os

BASIS_PATH = "universal_basis.pt"
REGISTRY_PATH = "skill_registry.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class IsotropicMemory:
    def __init__(self):
        try:
            self.basis = torch.load(BASIS_PATH, map_location=DEVICE)
        except:
            print("❌ Basis not found.")
            self.basis = None

        self.registry = {}
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r') as f:
                self.registry = json.load(f)

    def get_skill_vector(self, skill_name):
        if skill_name in self.registry:
            data = self.registry[skill_name]
            coeffs = torch.tensor(data["vector_coeffs"], device=DEVICE)
            # Project back to full space: coeffs @ basis
            # Basis shape: (16, 768)
            # Coeffs shape: (16)
            # Result: (768)
            return torch.matmul(coeffs, self.basis)
        return None
