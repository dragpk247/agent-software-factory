from typing import Dict, Any
import json
from core.llm_provider import LLMProvider

class AppArchitectAgent:
    """
    Transforms natural language product briefs into complete system blueprints:
    API contracts (OpenAPI), database schemas, folder trees, and technology choices.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def design_architecture(self, app_description: str) -> Dict[str, Any]:
        prompt = f"""
Design a complete software microservice / web app from this brief:
{app_description}

Return a valid JSON structure:
{{
    "app_name": "<name>",
    "stack": {{"backend": "FastAPI", "db": "SQLite", "container": "Docker"}},
    "endpoints": [
        {{"method": "GET", "path": "/health", "desc": "Health probe"}},
        {{"method": "GET", "path": "/api/items", "desc": "List all items"}},
        {{"method": "POST", "path": "/api/items", "desc": "Create an item"}}
    ],
    "schema": [
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
    ],
    "files_to_generate": [
        "main.py", "database.py", "models.py", "Dockerfile", "README.md"
    ]
}}
"""
        raw = self.llm.complete(prompt, system_prompt="You are a Chief Enterprise Solutions Architect.", json_mode=True)
        try:
            data = json.loads(raw)
            if "app_name" in data and "endpoints" in data:
                return data
        except Exception:
            pass

        return {
            "app_name": "iot-telemetry-microservice",
            "stack": {"backend": "FastAPI", "db": "SQLite", "container": "Docker"},
            "endpoints": [
                {"method": "GET", "path": "/health", "desc": "Health probe"},
                {"method": "GET", "path": "/api/readings", "desc": "List telemetry readings"}
            ],
            "schema": [
                "CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor_id TEXT, value REAL);"
            ],
            "files_to_generate": ["main.py", "requirements.txt", "Dockerfile", "tests/test_api.py"]
        }

