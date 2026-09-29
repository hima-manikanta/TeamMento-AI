from __future__ import annotations

import os
from typing import Any

import httpx


class HindsightService:
    def __init__(self) -> None:
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "")
        self.base_url = os.getenv("HINDSIGHT_BASE_URL", "").rstrip("/")
        self.timeout = float(os.getenv("HINDSIGHT_TIMEOUT", "10"))

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url)

    async def retain_experience(self, experience: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"stored": False, "provider": "disabled", "id": None}

        payload = {
            "experience": experience,
            "namespace": "teammento_hackathon",
            "kind": "mentor_resolution",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/experiences/retain",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            body = response.json()

        return {
            "stored": True,
            "provider": "hindsight",
            "id": body.get("id") or body.get("experience_id"),
            "raw": body,
        }

    async def recall_experience(
        self,
        *,
        concept: str,
        employee_level: str,
        task: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        if not self.enabled:
            return []

        payload = {
            "query": {
                "concept": concept,
                "employee_level": employee_level,
                "task": task,
            },
            "namespace": "teammento_hackathon",
            "kind": "mentor_resolution",
            "top_k": top_k,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/experiences/recall",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            body = response.json()

        if isinstance(body, list):
            return body
        if isinstance(body.get("results"), list):
            return body["results"]
        if isinstance(body.get("experiences"), list):
            return body["experiences"]
        return []
