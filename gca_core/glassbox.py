import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "gpt2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class GlassBox:
    def __init__(self):
        print(f"[🔮] Initializing GlassBox ({MODEL_ID})...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(DEVICE)
        self.layer_idx = 6 # Default for GPT2

    def generate_steered(self, prompt, steering_vec, strength, max_tokens=150):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)

        hook_handle = None
        if steering_vec is not None and strength != 0:
            steering_vec = steering_vec.to(DEVICE)
            def steer_hook(module, input, output):
                output[0][:, :, :] += steering_vec * strength
                return output

            layer = self.model.transformer.h[self.layer_idx]
            hook_handle = layer.register_forward_hook(steer_hook)

        try:
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
            response = self.tokenizer.decode(out[0], skip_special_tokens=True)
            return response
        finally:
            if hook_handle:
                hook_handle.remove()
