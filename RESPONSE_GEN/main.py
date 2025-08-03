from utils import load_requests
from runner import run_requests_concurrently
from reporter import print_summary
from config import CONCURRENCY
import asyncio

def main():
    # Load requests from ../LLM_REQUEST-GEN/generated/requests.json
    requests = load_requests()
    results = asyncio.run(run_requests_concurrently(requests, CONCURRENCY))
    print_summary(results)

if __name__ == "__main__":
    main()
