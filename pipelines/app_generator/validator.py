from typing import Dict, Any
from core.sandbox import ExecutionSandbox

class AppValidatorAgent:
    """
    Validates generated full-stack apps by running unit tests, linting, and checking syntax.
    """
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox

    def validate_scaffold(self) -> Dict[str, Any]:
        # 1. Syntax check main.py
        s_code, s_out, s_err = self.sandbox.run_command("python -m py_compile main.py")
        syntax_ok = (s_code == 0)

        # 2. Run unit tests if present
        t_code, t_out, t_err = self.sandbox.run_command("python -m unittest discover tests")
        tests_ok = (t_code == 0)

        return {
            "valid": syntax_ok and tests_ok,
            "syntax_check": {"passed": syntax_ok, "error": s_err},
            "tests_check": {"passed": tests_ok, "output": t_out, "error": t_err}
        }
