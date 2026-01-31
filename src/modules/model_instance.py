import os
from modules.ai_model import Model

ai = Model(
    os.getenv("base_url"),
    os.getenv("model"),
    os.getenv("api_key")
)
