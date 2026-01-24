import warnings

warnings.filterwarnings("ignore")


if __name__ == "__main__":
    import uvicorn

    try:
        from src.main import app

        print("=" * 50)
        print("Server starting on http://0.0.0.0:1178")
        print("Press Ctrl+C to stop")
        print("=" * 50)

        uvicorn.run(app, host="0.0.0.0", port=1178)

    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to exit...")
