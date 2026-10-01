import queue
import threading
import uuid
import time
from typing import Callable, Dict, Any, Optional

class QueueAdapter:
    """
    Decoupled task execution adapter.
    Operates initially as a local in-process worker queue.
    Designed for seamless drop-in replacement by the distributed_task_queue cluster (RESP client).
    """
    def __init__(self, mode: str = "local"):
        self.mode = mode
        self._local_queue = queue.Queue()
        self._results: Dict[str, Any] = {}
        self._running = True

    def submit_job(self, job_type: str, payload: Dict[str, Any]) -> str:
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        task = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "status": "queued",
            "enqueued_at": time.time()
        }
        self._local_queue.put(task)
        self._results[job_id] = task
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._results.get(job_id)

    def process_jobs(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Worker thread loop consuming tasks"""
        while self._running:
            try:
                task = self._local_queue.get(timeout=1.0)
                task["status"] = "processing"
                task["started_at"] = time.time()
                
                result = handler(task)
                
                task["status"] = "completed"
                task["result"] = result
                task["completed_at"] = time.time()
                self._results[task["id"]] = task
                self._local_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                self._results[task["id"]] = task

    def stop(self):
        self._running = False
