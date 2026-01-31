from typing import Union
import time
import os
from api_server.routes.completions import router as completion_router
# from api_server.routes.create_function import router as function_creation_router

from fastapi import FastAPI

app = FastAPI()


app.include_router(completion_router)
# app.include_router(function_creation_router)
# might not be good
