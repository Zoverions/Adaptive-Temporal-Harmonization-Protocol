import subprocess
import os
import sqlite3
from typing import Optional

class ToolBox:
    def __init__(self):
        self.unsafe_mode = False # Hard lock
        self._db_connections = {}

    def __del__(self):
        if hasattr(self, '_db_connections'):
            for conn in self._db_connections.values():
                try:
                    conn.close()
                except Exception:
                    pass

    def execute_python(self, code: str) -> str:
        """Executes Python code in a sandboxed subprocess."""
        # In production, use a real sandbox (e.g., Docker/Firecracker)
        # This is a basic implementation for the prototype
        try:
            # Dangerous! Only allowed if MoralKernel approved "REVERSIBLE" entropy
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Execution Error: {str(e)}"

    def query_database(self, query: str, db_path="demo.db") -> str:
        """Safe SQLite execution."""
        # Sanity check to prevent injection if Vector failed (belt & suspenders)
        if "DROP" in query.upper() or "DELETE" in query.upper():
            return "DB_ERROR: Destructive queries locked by ToolBox."

        try:
            if db_path not in self._db_connections:
                # check_same_thread=False allows reusing across threads, which is useful
                # if the ToolBox is invoked from different contexts.
                self._db_connections[db_path] = sqlite3.connect(db_path, check_same_thread=False)

            conn = self._db_connections[db_path]
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.commit()  # To ensure DML operations persist if executed, even though original didn't explicitly commit (it closed, which rolls back uncommitted)
            return str(rows)
        except Exception as e:
            if 'conn' in locals():
                try:
                    conn.rollback()
                except Exception:
                    pass
            return f"DB Error: {str(e)}"

    def file_op(self, operation: str, path: str, content: str = "") -> str:
        """Basic file system operations."""
        if operation == "READ":
            if os.path.exists(path):
                with open(path, 'r') as f: return f.read()
            return "FILE_ERROR: Not found."
        elif operation == "WRITE":
            # This is where Moral Kernel checks Irreversibility
            with open(path, 'w') as f: f.write(content)
            return "FILE_SUCCESS: Written."
        return "OP_ERROR: Unknown operation."
