import sys
from pathlib import Path

def _inject_shared_path():
    # adjust this to where your shared folder lives
    shared_path = Path(__file__).resolve().parent.parent.parent
    print(shared_path)
    if shared_path.exists():
        sys.path.insert(0, str(shared_path))
    else:
        raise RuntimeError(f"Shared path not found: {shared_path}")

_inject_shared_path()

from new_test_module.__main__ import main

if __name__ == "__main__":
    main()
