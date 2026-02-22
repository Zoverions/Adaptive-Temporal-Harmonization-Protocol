
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os

class TestIsotropicMemoryOptimization(unittest.TestCase):
    def setUp(self):
        # Ensure clean state for gca_core.memory
        if 'gca_core.memory' in sys.modules:
            del sys.modules['gca_core.memory']
        # Do not delete 'torch' if it's already there (though likely not in this env)
        # We will mock it using patch.dict

    def test_singleton_initialization(self):
        print("Testing Singleton Initialization...")

        # Create a mock for torch
        mock_torch = MagicMock()
        mock_torch.load = MagicMock()
        mock_torch.cuda = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        # Mock os.path.exists
        original_exists = os.path.exists
        def side_effect(path):
            if "universal_basis.pt" in path or "skill_registry.json" in path:
                return True
            return original_exists(path)

        # Patch sys.modules to inject our mock torch
        with patch.dict(sys.modules, {'torch': mock_torch}):
            # Now import the module under test inside the patch context
            # It will use the mocked torch
            try:
                from gca_core.memory import IsotropicMemory
            except ImportError as e:
                self.fail(f"Failed to import gca_core.memory: {e}")

            # Reset the singleton instance if it exists on the class
            # This is critical if tests run in same process
            if hasattr(IsotropicMemory, '_instance'):
                IsotropicMemory._instance = None

            # Patch open() and os.path.exists()
            with patch("builtins.open", mock_open(read_data='{"test": "data"}')) as mock_file:
                with patch("os.path.exists", side_effect=side_effect):

                    instances = []
                    # Instantiate multiple times
                    for i in range(5):
                        mem = IsotropicMemory()
                        instances.append(mem)
                        print(f"Instance {i+1} created")

                    # Verify Singleton Property
                    for i in range(1, 5):
                        self.assertIs(instances[0], instances[i], "Instances are not the same object (Singleton failed)")

                    # Verify Call Counts
                    torch_load_calls = mock_torch.load.call_count
                    open_calls = mock_file.call_count

                    print(f"torch.load called {torch_load_calls} times")
                    print(f"open() called {open_calls} times")

                    self.assertEqual(torch_load_calls, 1, f"torch.load should be called exactly once, but was called {torch_load_calls} times")
                    self.assertEqual(open_calls, 1, f"open() should be called exactly once, but was called {open_calls} times")

if __name__ == "__main__":
    unittest.main()
