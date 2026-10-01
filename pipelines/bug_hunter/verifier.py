from typing import Dict, Any
from core.sandbox import ExecutionSandbox

class BugVerifierAgent:
    """
    Executes the full test suite to guarantee:
    1. The reproduction test now passes.
    2. Zero regressions were introduced into existing test suites.
    """
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox

    def verify_patch(self, reproduction_test_cmd: str, full_suite_cmd: str) -> Dict[str, Any]:
        r_code, r_out, r_err = self.sandbox.run_command(reproduction_test_cmd)
        f_code, f_out, f_err = self.sandbox.run_command(full_suite_cmd)

        reproduction_passed = (r_code == 0)
        suite_passed = (f_code == 0)

        return {
            "verified": reproduction_passed and suite_passed,
            "reproduction_passed": reproduction_passed,
            "suite_passed": suite_passed,
            "reproduction_output": r_out,
            "suite_output": f_out
        }
