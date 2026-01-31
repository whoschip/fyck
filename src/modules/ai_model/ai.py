from openai import OpenAI
from pydantic import BaseModel
import json

class Model:
    def __init__(self, base_url, model, api_key):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

        self.tools = []
        self.tool_registry = {}

    def add_tool(self, fn, args_schema: BaseModel, description: str):
        tool_schema = {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": description,
                "parameters": args_schema.model_json_schema()
            }
        }

        self.tools.append(tool_schema)
        self.tool_registry[fn.__name__] = (fn, args_schema)

    def create_completion(self, messages: list):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]

            tool_name = tool_call.function.name
            raw_args = json.loads(tool_call.function.arguments)

            fn, schema = self.tool_registry[tool_name]

            args_obj = schema(**raw_args)

            result = fn(**args_obj.model_dump())

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return final_response.choices[0].message.content

        return msg.content
