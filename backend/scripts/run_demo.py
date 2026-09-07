"""Loopback-only demo convenience. The public deployment uses PostgreSQL."""
import os
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    demo_dir = root / ".demo"
    demo_dir.mkdir(exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite:///" + (demo_dir / "overview.sqlite3").as_posix()
    os.environ["LOCAL_DEMO"] = "true"
    os.environ["DEMO_MODE"] = "true"
    os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"
    import uvicorn
    from app.demo_app import create_demo_app
    print("FinTrack demo: http://localhost:5173/import")
    uvicorn.run(create_demo_app(), host="127.0.0.1", port=8000, access_log=False)


if __name__ == "__main__":
    main()
