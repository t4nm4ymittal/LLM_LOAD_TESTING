import os
from dotenv import load_dotenv
from client.euri_client import EURIClient
from cli.interactive_cli import run_cli

load_dotenv()

def main():
    api_key = os.getenv("EURI_API_KEY") or input("Enter EURI API key: ").strip()
    model = os.getenv("EURI_MODEL", "gpt-4.1-nano")

    if not api_key:
        print("❌ API key is required")
        return

    client = EURIClient(api_key)
    run_cli(client, model)

if __name__ == "__main__":
    main()
