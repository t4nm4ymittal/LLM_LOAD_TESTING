import json
from typing import Dict, Any, Optional

def create_generation_prompt(sample_request: Dict[str, Any], num_variations: int = 10) -> str:
    """Create a strict prompt for generating request variations"""
    
    method = sample_request.get('method', 'GET')
    base_url = sample_request.get('base_url', '')
    endpoint = sample_request.get('endpoint', '')
    path_vars = sample_request.get('path_variables', {})
    query_params = sample_request.get('query_parameters', {})
    headers = sample_request.get('headers', {})
    body = sample_request.get('body')
    
    # Build full URL example
    full_url_example = base_url + endpoint
    if path_vars:
        for var_name, var_value in path_vars.items():
            full_url_example = full_url_example.replace(f"{{{var_name}}}", str(var_value))
    
    if query_params:
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        full_url_example += f"?{query_string}"
    
    prompt = f"""You are a load testing expert. Generate EXACTLY {num_variations} realistic variations of the given HTTP request.

SAMPLE REQUEST STRUCTURE:
Method: {method}
Base URL: {base_url}
Endpoint: {endpoint}
Full URL Example: {full_url_example}"""

    if path_vars:
        prompt += f"\n\nPATH VARIABLES TO VARY:"
        for var_name, sample_value in path_vars.items():
            prompt += f"\n- {var_name}: {sample_value} (generate different realistic values)"

    if query_params:
        prompt += f"\n\nQUERY PARAMETERS TO VARY:"
        for param_name, sample_value in query_params.items():
            prompt += f"\n- {param_name}: {sample_value} (generate different realistic values)"

    if headers:
        prompt += f"\n\nHEADERS (keep exactly as shown):\n{json.dumps(headers, indent=2)}"

    if body is not None:
        prompt += f"\n\nBODY STRUCTURE (vary the data, keep structure):\n{json.dumps(body, indent=2)}"
    else:
        prompt += f"\n\nBODY: None (DO NOT include body in generated requests)"

    body_instruction = "Keep body structure identical, only vary the data values" if body is not None else "DO NOT include body field in any generated request."
    
    prompt += f"""

STRICT REQUIREMENTS:
1. Generate EXACTLY {num_variations} request variations
2. ONLY vary the specified path variables and query parameters with realistic values
3. Keep headers EXACTLY as provided - do not add, remove, or modify
4. {body_instruction}
5. Generate requests where the "body" field is a **JSON object**, not a stringified JSON string.
5. Each full URL must be properly constructed: base_url + endpoint_with_path_vars + query_params
6. Return ONLY a valid JSON array, no other text

RESPONSE FORMAT:"""
    
    # Build the response format example
    example_request = {
        "method": method,
        "url": "complete_url_with_path_vars_and_query_params",
        "headers": headers if headers else {}
    }
    
    if body is not None:
        example_request["body"] = "..."
    
    prompt += f"""
[
  {json.dumps(example_request, indent=4)}
]

Generate realistic variations for:"""

    if path_vars:
        prompt += f"\n- Path variables: {list(path_vars.keys())}"
    if query_params:
        prompt += f"\n- Query parameters: {list(query_params.keys())}"
    if body is not None:
        prompt += f"\n- Body data values (maintain structure)"

    prompt += f"\n\nGenerate {num_variations} variations now:"

    return prompt