import subprocess
import os
import shutil
from typing import Tuple, Optional

class ExecutionSandbox:
    """
    Manages isolated execution of agent-generated commands and tests.
    Supports either Docker containerized execution (Option 4) or direct local process execution.
    """
    def __init__(self, use_docker: bool = False, container_name: str = "agent_sandbox_worker", local_workspace: str = "./workspace"):
        self.use_docker = use_docker
        self.container_name = container_name
        self.local_workspace = os.path.abspath(local_workspace)
        os.makedirs(self.local_workspace, exist_ok=True)

    def run_command(self, cmd: str, cwd: Optional[str] = None, timeout: int = 120) -> Tuple[int, str, str]:
        """
        Executes a shell command either inside the Docker sandbox or locally.
        Returns: (exit_code, stdout, stderr)
        """
        if self.use_docker:
            workdir = cwd or "/workspace"
            exec_cmd = ["docker", "exec", "-w", workdir, self.container_name, "bash", "-c", cmd]
            try:
                proc = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=timeout)
                return proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired:
                return -1, "", f"Command timed out after {timeout} seconds"
            except Exception as e:
                return -1, "", str(e)
        else:
            target_cwd = cwd or self.local_workspace
            try:
                proc = subprocess.run(cmd, shell=True, cwd=target_cwd, capture_output=True, text=True, timeout=timeout)
                return proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired:
                return -1, "", f"Command timed out after {timeout} seconds"
            except Exception as e:
                return -1, "", str(e)

    def write_file(self, rel_path: str, content: str):
        full_path = os.path.join(self.local_workspace, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_file(self, rel_path: str) -> Optional[str]:
        full_path = os.path.join(self.local_workspace, rel_path)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def clean_workspace(self):
        if os.path.exists(self.local_workspace):
            shutil.rmtree(self.local_workspace)
        os.makedirs(self.local_workspace, exist_ok=True)
