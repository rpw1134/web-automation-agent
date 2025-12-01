import uvicorn

def dev() -> None:
    """Development server entry point."""
    uvicorn.run(
        "agent_backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    dev()