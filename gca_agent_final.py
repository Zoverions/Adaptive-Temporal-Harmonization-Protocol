from gca_core.glassbox import GlassBox
from gca_core.memory import IsotropicMemory
from gca_core.optimizer import GCAOptimizer
from gca_core.moral import MoralKernel, Action, EntropyClass
from gca_core.tools import ToolBox
import re

def parse_tool_call(response):
    """
    Extracts code blocks or tool commands from the model's text output.
    Regex looks for: ```python ... ``` or SQL queries.
    """
    # SQL Detection
    if "SELECT" in response.upper() and "FROM" in response.upper():
        return "SQL", response.strip()

    # Python Detection
    code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
    if code_match:
        return "PYTHON", code_match.group(1).strip()

    return "TEXT", response

def main():
    print("="*60)
    print("GCA v1.2: The Autonomous Agent")
    print("="*60)

    # 1. Init System
    gb = GlassBox()
    mem = IsotropicMemory()
    opt = GCAOptimizer(gb, mem)
    moral = MoralKernel()
    tools = ToolBox()

    # 2. User Input
    # This prompt implies a tool (SQL) is needed
    # Using a more explicit SQL prompt to ensure routing works with the basic SVD basis
    prompt = "SELECT name, active FROM users WHERE active = 1;"
    print(f"\nUSER: {prompt}")

    # 3. Geometric Routing (Think)
    # The geometric router detects 'SQL' intent from the prompt shape
    detected_skill = opt.route(prompt)
    print(f"[🧭] Geometric Intent: {detected_skill}")

    if detected_skill == "NONE":
        print("No skill detected. Exiting.")
        return

    # 4. Vector Loading & Tuning
    vec = mem.get_skill_vector(detected_skill)
    strength = opt.auto_tune(prompt, vec)
    print(f"[🔧] Latent Pressure: {strength}")

    # 5. Steered Generation (Reasoning)
    # The model generates the PLAN/CODE while steered by the vector
    response = gb.generate_steered(prompt, vec, strength, max_tokens=150)
    print(f"\n[🧠] Model Thought:\n{response}")

    # 6. Tool Parsing & Moral Audit (The Filter)
    tool_type, content = parse_tool_call(response)

    if tool_type == "TEXT":
        print("[📢] Result: Just text, no action taken.")
        return

    print(f"\n[🛠️] Tool Request: {tool_type}")

    # CLASSIFY ENTROPY
    # We map the tool request to the Thermodynamic Entropy Classes
    entropy = EntropyClass.REVERSIBLE
    if tool_type == "PYTHON":
        entropy = EntropyClass.BOUNDED # Code execution is risky but contained
    if "DELETE" in content.upper() or "DROP" in content.upper():
        entropy = EntropyClass.IRREVERSIBLE # Data loss is high entropy

    # MORAL CHECK
    # Added agents_affected=1 to match Action definition
    # Lowered harm to 0.3 to allow REVERSIBLE actions but potentially block IRREVERSIBLE ones
    action = Action(f"execute_{tool_type}", content[:50], 0.3, 0.9, 0.2, 1.0, 1, entropy)
    # evaluate returns (approved, reason)
    ok, reason = moral.evaluate([action])

    if not ok:
        print(f"[🛡️] BLOCKED by Moral Kernel: {reason}")
        return

    # 7. Execution (The Hands)
    print(f"[✅] Moral Check Passed. Executing...")

    result = ""
    if tool_type == "SQL":
        # For demo, create a dummy DB if missing
        import sqlite3
        conn = sqlite3.connect("demo.db")
        conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, active BOOLEAN)")
        conn.execute("INSERT INTO users VALUES ('Alice', 1), ('Bob', 0)")
        conn.commit()
        conn.close()

        result = tools.query_database(content)

    elif tool_type == "PYTHON":
        result = tools.execute_python(content)

    print(f"\n[💻] SYSTEM OUTPUT:\n{result}")

if __name__ == "__main__":
    main()
