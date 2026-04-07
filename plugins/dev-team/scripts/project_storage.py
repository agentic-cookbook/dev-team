#!/usr/bin/env python3
"""Project storage — thin wrapper around storage-provider.

Kept for backwards compatibility. Callers should migrate to storage_provider.py.

Usage: project_storage.py <resource> <action> [--flags]
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from storage_provider import dispatch


def main():
    if len(sys.argv) < 3:
        print("Usage: project_storage.py <resource> <action> [flags]", file=sys.stderr)
        sys.exit(1)

    resource = sys.argv[1]
    action = sys.argv[2]
    flags = sys.argv[3:]

    backend = os.environ.get("PROJECT_STORAGE_BACKEND",
                os.environ.get("STORAGE_PROVIDER_BACKEND", "markdown"))
    dispatch(resource, action, flags, backend=backend)


if __name__ == "__main__":
    main()
