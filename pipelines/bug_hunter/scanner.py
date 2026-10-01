import os
import ast
from typing import List, Dict, Any

class BugScannerAgent:
    """
    Performs static analysis, code smell detection, and security pattern scanning.
    """
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = os.path.abspath(workspace_path)

    def scan_codebase(self) -> List[Dict[str, Any]]:
        findings = []
        for root, _, files in os.walk(self.workspace_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.workspace_path)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        tree = ast.parse(content)
                        # Check for empty except clauses or division by zero risks
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ExceptHandler) and node.type is None:
                                findings.append({
                                    "file": rel_path,
                                    "line": node.lineno,
                                    "severity": "MEDIUM",
                                    "type": "bare_except",
                                    "description": "Bare except clause catches SystemExit and KeyboardInterrupt."
                                })
                            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                                findings.append({
                                    "file": rel_path,
                                    "line": node.lineno,
                                    "severity": "HIGH",
                                    "type": "division_risk",
                                    "description": "Division operation without explicit zero divisor guard."
                                })
                    except Exception as e:
                        findings.append({
                            "file": rel_path,
                            "line": 0,
                            "severity": "CRITICAL",
                            "type": "syntax_error",
                            "description": str(e)
                        })
        return findings
