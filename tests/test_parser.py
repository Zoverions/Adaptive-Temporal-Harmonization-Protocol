
import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock dependencies to allow importing gca_agent_final
sys.modules['gca_core.glassbox'] = MagicMock()
sys.modules['gca_core.memory'] = MagicMock()
sys.modules['gca_core.optimizer'] = MagicMock()
sys.modules['gca_core.moral'] = MagicMock()
sys.modules['gca_core.tools'] = MagicMock()
sys.modules['torch'] = MagicMock()

from gca_agent_final import parse_tool_call

class TestParser(unittest.TestCase):
    def test_sql_detection(self):
        response = "SELECT * FROM users;"
        tool_type, content = parse_tool_call(response)
        self.assertEqual(tool_type, "SQL")
        self.assertEqual(content, "SELECT * FROM users;")

    def test_python_detection(self):
        response = "Check this out: ```python\nprint('hello')\n```"
        tool_type, content = parse_tool_call(response)
        self.assertEqual(tool_type, "PYTHON")
        self.assertEqual(content, "print('hello')")

    def test_text_only(self):
        response = "This is just a normal response."
        tool_type, content = parse_tool_call(response)
        self.assertEqual(tool_type, "TEXT")
        self.assertEqual(content, response)

    def test_sql_case_insensitivity(self):
        response = "select name from employees"
        tool_type, content = parse_tool_call(response)
        self.assertEqual(tool_type, "SQL")
        self.assertEqual(content, response)

    def test_multiline_python(self):
        response = "```python\nimport os\nprint(os.getcwd())\n```"
        tool_type, content = parse_tool_call(response)
        self.assertEqual(tool_type, "PYTHON")
        self.assertEqual(content, "import os\nprint(os.getcwd())")

if __name__ == "__main__":
    unittest.main()
