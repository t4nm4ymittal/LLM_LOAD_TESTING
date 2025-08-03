import json
from pathlib import Path

# Correct path to your LLM-generated request file
REQUESTS_PATH = (
    Path(__file__)
    .resolve()                                  # Absolute path of utils.py
    .parent                                     # /load_tester
    .parent / "LLM-REQUEST_GEN" / "generated" / "requests_generated.json"
)

def load_requests(file_path=REQUESTS_PATH):
    if not file_path.exists():
        raise FileNotFoundError(f"Request file not found at: {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)['requests']
