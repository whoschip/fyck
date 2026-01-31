import uvicorn
from dotenv import load_dotenv


# temp like this
if __name__ == "__main__":
    uvicorn.run(
        "api_server.serve:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
