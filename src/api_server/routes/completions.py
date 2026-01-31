import os
import time
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from modules.model_instance import ai

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    completion_dict: List[Message]


@router.post("/completion")
async def new_completion(payload: dict):
    start_time = time.perf_counter()

    try:
        messages = payload["completion_dict"]

        response = await ai.create_completion(messages)

        end_time = time.perf_counter()

        return {
            "status": "ok",
            "response": response,
            "time_taken": f"{round(end_time - start_time)}s",
        }

    except Exception as e:
        end_time = time.perf_counter()

        return {
            "status": "error",
            "error": str(e),
            "time_taken": f"{round(end_time - start_time)}s",
        }
