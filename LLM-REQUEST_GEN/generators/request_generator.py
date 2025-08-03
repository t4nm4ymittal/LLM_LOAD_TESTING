import json
import re

class RequestGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate(self, prompt_messages, model):
        """Generate request variations using LLM"""
        raw_output = self.llm_client.generate_completion(prompt_messages, model)

        if not raw_output:
            print("[RequestGenerator] No output received from LLM")
            return []

        try:
            # Clean the output
            cleaned = self._clean_llm_output(raw_output)
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate structure
            if not isinstance(data, list):
                print("[RequestGenerator] Expected list of requests, got:", type(data))
                return []
            
            # Validate each request
            validated_requests = []
            for i, request in enumerate(data):
                if self._validate_request(request, i):
                    validated_requests.append(request)
            
            print(f"[RequestGenerator] Generated {len(validated_requests)} valid requests")
            return validated_requests
            
        except json.JSONDecodeError as e:
            print(f"[RequestGenerator] JSON parsing error: {e}")
            print(f"[RequestGenerator] Raw output preview: {raw_output[:200]}...")
            return []

    def _clean_llm_output(self, raw_output):
        """Clean LLM output to extract JSON"""
        # Remove markdown code blocks
        cleaned = re.sub(r'```(?:json)?\s*', '', raw_output)
        cleaned = re.sub(r'```\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Remove any text before the first '[' and after the last ']'
        start_idx = cleaned.find('[')
        end_idx = cleaned.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
        
        return cleaned.strip()

    def _validate_request(self, request, index):
        """Validate individual request structure"""
        if not isinstance(request, dict):
            print(f"[RequestGenerator] Request {index}: Not a dictionary")
            return False
        
        # Check required fields
        required_fields = ['method', 'url']
        for field in required_fields:
            if field not in request:
                print(f"[RequestGenerator] Request {index}: Missing required field '{field}'")
                return False
        
        # Validate method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if request['method'].upper() not in valid_methods:
            print(f"[RequestGenerator] Request {index}: Invalid HTTP method '{request['method']}'")
            return False
        
        # Validate URL
        if not isinstance(request['url'], str) or not request['url'].strip():
            print(f"[RequestGenerator] Request {index}: Invalid URL")
            return False
        
        # Validate headers (optional)
        if 'headers' in request and not isinstance(request['headers'], dict):
            print(f"[RequestGenerator] Request {index}: Headers must be a dictionary")
            return False
        
        # Validate body (optional)
        if 'body' in request and request['body'] is not None:
            # Body can be dict, list, or string
            if not isinstance(request['body'], (dict, list, str)):
                print(f"[RequestGenerator] Request {index}: Invalid body type")
                return False
        
        return True

    def get_generation_stats(self, requests):
        """Get statistics about generated requests"""
        if not requests:
            return {"total": 0}
        
        stats = {
            "total": len(requests),
            "methods": {},
            "has_headers": 0,
            "has_body": 0,
            "unique_urls": len(set(req['url'] for req in requests))
        }
        
        for request in requests:
            # Count methods
            method = request['method'].upper()
            stats["methods"][method] = stats["methods"].get(method, 0) + 1
            
            # Count requests with headers/body
            if request.get('headers'):
                stats["has_headers"] += 1
            if request.get('body') is not None:
                stats["has_body"] += 1
        
        return stats