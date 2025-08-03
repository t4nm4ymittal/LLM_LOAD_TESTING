import json
from utils.io_utils import save_requests
from prompts.request_prompt import create_generation_prompt
from generators.request_generator import RequestGenerator

def extract_path_variables(endpoint):
    """Extract path variables from endpoint string"""
    import re
    # Find all {variable} patterns
    path_vars = re.findall(r'\{([^}]+)\}', endpoint)
    return path_vars

def extract_query_parameters(endpoint):
    """Extract query parameters from endpoint string"""
    from urllib.parse import urlparse, parse_qs
    
    # Parse the endpoint to get query parameters
    parsed = urlparse(endpoint)
    if parsed.query:
        query_dict = parse_qs(parsed.query, keep_blank_values=True)
        # Convert list values to single values (parse_qs returns lists)
        return {k: v[0] if v else '' for k, v in query_dict.items()}
    return {}

def collect_path_variables(endpoint):
    """Collect path variable values from user"""
    path_vars = {}
    detected_vars = extract_path_variables(endpoint)
    
    if not detected_vars:
        return path_vars
    
    print(f"\n🔗 Path Variables detected in endpoint: {detected_vars}")
    print("Please provide sample values for each path variable:")
    
    for var_name in detected_vars:
        while True:
            value = input(f"  {var_name}: ").strip()
            if value:
                path_vars[var_name] = value
                break
            else:
                print(f"    Please provide a value for {var_name}")
    
    return path_vars

def collect_query_parameters(endpoint):
    """Collect query parameter values from user"""
    query_params = {}
    detected_params = extract_query_parameters(endpoint)
    
    print(f"\n❓ Query Parameters")
    
    # Handle existing parameters in endpoint
    if detected_params:
        print(f"Detected parameters in endpoint: {list(detected_params.keys())}")
        print("Current values (press Enter to keep, or provide new value):")
        
        for param_name, current_value in detected_params.items():
            new_value = input(f"  {param_name} (current: '{current_value}'): ").strip()
            query_params[param_name] = new_value if new_value else current_value
    
    # Allow adding additional parameters
    print("\nAdd additional query parameters (name:value), press Enter twice to finish:")
    while True:
        line = input("Additional Parameter: ").strip()
        if not line:
            break
        if ":" in line:
            name, value = map(str.strip, line.split(":", 1))
            if name not in query_params:  # Don't override existing
                query_params[name] = value
            else:
                print(f"Parameter '{name}' already exists, skipping...")
        else:
            print("Format should be: paramName:paramValue")
    
    return query_params

def collect_headers():
    """Collect headers from user"""
    headers = {}
    print("\n📋 Headers")
    print("Enter headers (key:value), press Enter twice to finish:")
    
    while True:
        line = input("Header: ").strip()
        if not line:
            break
        if ":" in line:
            k, v = map(str.strip, line.split(":", 1))
            headers[k] = v
        else:
            print("Format should be: HeaderName:HeaderValue")
    
    return headers

def collect_body():
    """Collect request body from user"""
    print("\n📄 Request Body")
    body_input = input("Body (JSON string or leave blank for no body): ").strip()
    
    if not body_input:
        return None
    
    try:
        return json.loads(body_input)
    except json.JSONDecodeError:
        print("⚠️  Invalid JSON format, treating as plain text")
        return {"data": body_input}

def run_cli(client, model):
    print("📋 Enhanced Load Testing Request Generator CLI\n")
    
    # Collect basic request info
    method = input("HTTP Method (default: GET): ").strip().upper() or "GET"
    base_url = input("Base URL (e.g., https://api.example.com): ").strip()
    endpoint = input("Endpoint path (e.g., /users or /users/{userId}): ").strip()
    
    # Collect path variables (auto-detected from endpoint)
    path_vars = collect_path_variables(endpoint)
    
    # Collect query parameters (auto-detected + additional)
    query_params = collect_query_parameters(endpoint)
    
    # Collect headers
    headers = collect_headers()
    
    # Collect body (only if user wants it)
    body = None
    if method.upper() in ['POST', 'PUT', 'PATCH']:
        include_body = input("Include request body? (y/N): ").strip().lower() == 'y'
        if include_body:
            body = collect_body()
    
    # Build sample request
    sample_request = {
        "method": method,
        "base_url": base_url,
        "endpoint": endpoint,
        "path_variables": path_vars,
        "query_parameters": query_params,
        "headers": headers,
        "body": body
    }
    
    # Show sample request summary
    print("\n📋 Sample Request Summary:")
    print(f"Method: {method}")
    print(f"Base URL: {base_url}")
    print(f"Endpoint: {endpoint}")
    if path_vars:
        print(f"Path Variables: {path_vars}")
    if query_params:
        print(f"Query Parameters: {query_params}")
    if headers:
        print(f"Headers: {headers}")
    if body is not None:
        print(f"Body: {json.dumps(body, indent=2)}")
    else:
        print("Body: None")
    
    # Confirm and generate
    confirm = input("\nProceed with generation? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Generation cancelled")
        return
    
    num = int(input("How many variations? [5]: ") or "5")
    
    generator = RequestGenerator(client)
    prompt = create_generation_prompt(sample_request, num)
    print(f"📝 Generating {num} request variations...")
    
    requests = generator.generate(prompt, model)
    
    if requests:
        print(f"✅ {len(requests)} requests generated successfully")
        
        # Show first request as preview
        if requests:
            print("\n📋 Preview of first generated request:")
            print(json.dumps(requests[0], indent=2))
        
        save = input("\nSave to file? (Y/n): ").strip().lower() != 'n'
        if save:
            filename = input("Filename (default: requests_generated.json): ").strip() or "requests_generated.json"
            filepath = save_requests(requests, filename)
            print(f"💾 Saved to {filepath}")
    else:
        print("❌ Failed to generate requests")