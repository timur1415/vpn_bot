import uvicorn

from server.fastapi_init import init_fastapi_app

app = init_fastapi_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )