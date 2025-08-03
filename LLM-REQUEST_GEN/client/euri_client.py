import requests

class EURIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.euron.one/api/v1/euri/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def generate_completion(self, prompt: str, model: str) -> str:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model
        }
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"[EURIClient] Error: {e}")
            return None
