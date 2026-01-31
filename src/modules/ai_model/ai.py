import asyncio
import inspect
import json

from openai import OpenAI
from pydantic import BaseModel


class Model:
    def __init__(
        self,
        base_url,
        model,
        api_key,
        request_timeout: int = 30,
        tool_timeout: int = 30,
        max_tool_loops: int = 3,
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

        self.tools = []
        self.tool_registry = {}
        self.request_timeout = request_timeout
        self.tool_timeout = tool_timeout
        self.max_tool_loops = max_tool_loops

    def list_tools(self):
        return self.tools

    def add_tool(self, fn, args_schema: BaseModel, description: str):
        tool_schema = {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": description,
                "parameters": args_schema.model_json_schema(),
            },
        }

        self.tools.append(tool_schema)
        self.tool_registry[fn.__name__] = (fn, args_schema)

    def add_dynamic_tool(self, tool_name: str, fn, schema: dict):
        self.tools.append(schema)
        self.tool_registry[tool_name] = (fn, None)

    async def _call_model(self, messages: list, tools):
        return await asyncio.wait_for(
            asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
            ),
            timeout=self.request_timeout,
        )

    async def create_completion(self, messages: list):
        response = await self._call_model(messages, self.tools if self.tools else None)

        msg = response.choices[0].message

        loop_count = 0
        while msg.tool_calls:
            loop_count += 1
            if loop_count > self.max_tool_loops:
                raise TimeoutError("Tool call loop exceeded max_tool_loops")

            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                raw_args = json.loads(tool_call.function.arguments)

                if tool_name not in self.tool_registry:
                    raise Exception(f"Tool not registered: {tool_name}")

                fn, schema = self.tool_registry[tool_name]

                if schema:
                    args_obj = schema(**raw_args)
                    args = args_obj.model_dump()
                else:
                    args = raw_args

                if inspect.iscoroutinefunction(fn):
                    result = await asyncio.wait_for(fn(**args), timeout=self.tool_timeout)
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(fn, **args),
                        timeout=self.tool_timeout,
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            response = await self._call_model(messages, self.tools)
            msg = response.choices[0].message

        return msg.content
