from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from modules.model_instance import ai

router = APIRouter()


async def get_weather(location: str):
    return {"location": location, "temp": 100}

ALLOWED_FUNCTIONS = {
    "get_weather": get_weather,
    "get_time": lambda zone: {"zone": zone, "time": "12:00PM"}
}

REGISTERED_TOOLS = {}



class ToolCreateRequest(BaseModel):
    tool_name: str
    description: str
    parameters: Dict[str, Any]
    handler: str



@router.post("/tools/register")
async def register_tool(req: ToolCreateRequest):

    if req.handler not in ALLOWED_FUNCTIONS:
        raise HTTPException(status_code=400, detail="Handler not allowed")

    if req.tool_name in REGISTERED_TOOLS:
        raise HTTPException(status_code=400, detail="Tool already exists")

    tool_schema = {
        "type": "function",
        "function": {
            "name": req.tool_name,
            "description": req.description,
            "parameters": req.parameters
        }
    }

    fn = ALLOWED_FUNCTIONS[req.handler]

    REGISTERED_TOOLS[req.tool_name] = {
        "schema": tool_schema,
        "fn": fn
    }

    ai.add_dynamic_tool(
        tool_name=req.tool_name,
        fn=fn,
        schema=tool_schema
    )

    return {
        "status": "ok",
        "tool": req.tool_name
    }



@router.get("/tools/list")
async def list_tools():
    return {
        "status": "ok",
        "tools": list(REGISTERED_TOOLS.keys())
    }
