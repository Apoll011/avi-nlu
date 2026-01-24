import sys
import os
import warnings

warnings.filterwarnings("ignore")


def apply_numpy_fix():
    """Apply numpy compatibility fix for older code"""
    try:
        import numpy as np

        if not hasattr(np, "float"):
            np.float = float
            np.float_ = np.float64

        if not hasattr(np, "int"):
            np.int = int
            np.int_ = np.int64

        if not hasattr(np, "bool"):
            np.bool = bool

        if not hasattr(np, "complex"):
            np.complex = complex

            print("[OK] Numpy compatibility patch applied")

    except ImportError:
        print("[WARNING] Numpy not found, skipping patch")
    except Exception as e:
        print(f"[WARNING] Could not apply numpy patch: {e}")


apply_numpy_fix()

if __name__ == "__main__":
    import uvicorn

    try:
        from main import app

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
