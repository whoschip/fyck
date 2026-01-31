from typing import Union
from modules.ai_model import Model
import time
import os

from fastapi import FastAPI

app = FastAPI()

ai = Model(os.getenv("base_url"), os.getenv("model"), os.getenv("api_key"))

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/send")
async def new_completion(payload: dict):
    try:
        start_time = time.perf_counter()

        messages = payload["completion_dict"]

        response = ai.create_completion(messages)

        end_time = time.perf_counter()
        return {
            "status": "ok",
            "response": response,
            "time_taken" : f"{round(end_time - start_time)}s"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "time_taken" : f"{round(end_time - start_time)}s"
        }


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}