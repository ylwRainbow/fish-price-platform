import argparse
import sys
import os
import selenium
from .sample_test import run_sample


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("UI_BASE_URL"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(f"selenium {selenium.__version__}")
        sys.exit(0)
    base_url = args.base_url or "http://127.0.0.1:8000"
    run_sample(base_url)


if __name__ == "__main__":
    main()
