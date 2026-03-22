
import torch
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
import sys

# Ensure current directory and gca_core are in path
sys.path.append(os.getcwd())

from gca_optimizer import GCAOptimizer

class TestGCAOptimizerBatchDecode(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_tokenizer = MagicMock()
        self.mock_basis = MagicMock()

        # Mock registry data
        self.registry_data = {
            "SQL": {"vector_coeffs": [0.1] * 16},
            "CORPORATE": {"vector_coeffs": [0.2] * 16}
        }
        self.registry_json = json.dumps(self.registry_data)

    @patch('builtins.open', new_callable=mock_open)
    @patch('gca_optimizer.torch.tensor')
    def test_auto_tune_strength_uses_batch_decode(self, mock_tensor, mock_file):
        mock_file.return_value.__enter__.return_value.read.return_value = self.registry_json

        optimizer = GCAOptimizer(self.mock_model, self.mock_tokenizer, self.mock_basis)

        prompt = "test prompt"
        skill_vec = torch.randn(768)

        # Mock tokenizer call in auto_tune_strength
        self.mock_tokenizer.return_value = {
            "input_ids": torch.zeros((1, 5), dtype=torch.long),
            "attention_mask": torch.ones((1, 5), dtype=torch.long)
        }

        # Mock model.generate output (batch of 4)
        mock_out = torch.zeros((4, 10), dtype=torch.long)
        self.mock_model.generate.return_value = mock_out

        # Mock batch_decode to return specific strings to test repetition logic
        # 1 & 2: Diverse, 3: Repetitive, 4: Diverse (should not be reached if 3 fails)
        self.mock_tokenizer.batch_decode.return_value = [
            "word1 word2 word3 word4 word5", # Ratio 1.0
            "apple banana orange grape pear", # Ratio 1.0
            "repeat repeat repeat repeat repeat", # Ratio 0.2 (< 0.6)
            "this should be skipped"
        ]

        with patch('builtins.print'):
            best_strength = optimizer.auto_tune_strength(prompt, skill_vec)

        # Verify batch_decode was called instead of decode
        self.mock_tokenizer.batch_decode.assert_called_once_with(mock_out, skip_special_tokens=True)
        self.assertEqual(self.mock_tokenizer.decode.call_count, 0)

        # Verify the best strength was the one before the repetitive one
        # candidates are [2.0, 4.0, 6.0, 8.0]
        # 2.0 (OK), 4.0 (OK), 6.0 (Repetitive -> Break)
        self.assertEqual(best_strength, 4.0)

if __name__ == '__main__':
    unittest.main()
