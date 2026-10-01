import socket
import json
import time
from typing import Optional, Dict, Any

class DistributedTaskQueueClient:
    """
    Lightweight, direct RESP socket client for connecting this Software Factory
    to your Rust distributed_task_queue engine (running on 127.0.0.1:6379).
    
    Implements:
    - LPUSH: Schedule factory jobs
    - RPOPLEASE: Lease job with visibility timeout (prevents lost tasks)
    - TASKACK: Confirm successful job completion
    - TASKNACK: Fail and escalate to Dead-Letter Queue (DLQ)
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.sock: Optional[socket.socket] = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        if self.password:
            self._send_command(f"AUTH {self.password}")
            self._read_response()

    def _send_command(self, cmd_str: str):
        parts = cmd_str.split(" ")
        resp = f"*{len(parts)}\r\n"
        for p in parts:
            resp += f"${len(p)}\r\n{p}\r\n"
        self.sock.sendall(resp.encode("utf-8"))

    def _read_response(self) -> str:
        data = self.sock.recv(4096).decode("utf-8")
        return data

    def push_factory_job(self, queue_name: str, job_payload: Dict[str, Any]):
        serialized = json.dumps(job_payload).replace(" ", "_")
        self._send_command(f"LPUSH {queue_name} {serialized}")
        return self._read_response()

    def lease_factory_job(self, queue_name: str, visibility_secs: int = 60) -> Optional[str]:
        self._send_command(f"RPOPLEASE {queue_name} {visibility_secs}")
        resp = self._read_response()
        if "$-1" in resp or "nil" in resp:
            return None
        return resp

    def ack_job(self, queue_name: str, task_id: str):
        self._send_command(f"TASKACK {queue_name} {task_id}")
        return self._read_response()

    def nack_job(self, queue_name: str, task_id: str):
        self._send_command(f"TASKNACK {queue_name} {task_id}")
        return self._read_response()

    def close(self):
        if self.sock:
            self.sock.close()
