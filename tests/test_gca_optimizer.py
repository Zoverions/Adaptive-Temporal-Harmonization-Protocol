
import torch
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
import sys

# Ensure parent directory is in path so we can import gca_optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gca_optimizer import GCAOptimizer, DEVICE

class TestGCAOptimizer(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_tokenizer = MagicMock()
        self.mock_basis = MagicMock()

        # Determine path to skill_registry.json
        # Assuming the test is run from repo root or tests/
        # We need to find where skill_registry.json is relative to this file.
        # This file is in tests/
        # skill_registry.json is in root/
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        registry_path = os.path.join(root_dir, "skill_registry.json")

        with open(registry_path, "r") as f:
            self.registry_data = json.load(f)

    def test_route_intent_sql(self):
        optimizer = GCAOptimizer(self.mock_model, self.mock_tokenizer, self.mock_basis)

        # Mock get_prompt_geometry to return the SQL vector exactly
        sql_vec = torch.tensor(self.registry_data["SQL"]["vector_coeffs"], device=DEVICE)
        optimizer.get_prompt_geometry = MagicMock(return_value=sql_vec.unsqueeze(0))

        with patch('builtins.print'):
            skill = optimizer.route_intent("select * from table")

        self.assertEqual(skill, "SQL")

    def test_route_intent_corporate(self):
        optimizer = GCAOptimizer(self.mock_model, self.mock_tokenizer, self.mock_basis)

        corporate_vec = torch.tensor(self.registry_data["CORPORATE"]["vector_coeffs"], device=DEVICE)
        optimizer.get_prompt_geometry = MagicMock(return_value=corporate_vec.unsqueeze(0))

        with patch('builtins.print'):
            skill = optimizer.route_intent("synergy leverage")
        self.assertEqual(skill, "CORPORATE")

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_empty_registry(self, mock_file):
        # Re-instantiate with empty registry
        optimizer = GCAOptimizer(self.mock_model, self.mock_tokenizer, self.mock_basis)

        self.assertEqual(optimizer.skill_names, [])
        self.assertIsNone(optimizer.skill_matrix)

        optimizer.get_prompt_geometry = MagicMock(return_value=torch.randn(1, 16))

        with patch('builtins.print'):
            skill = optimizer.route_intent("test")

        self.assertEqual(skill, "NONE")

if __name__ == '__main__':
    unittest.main()
