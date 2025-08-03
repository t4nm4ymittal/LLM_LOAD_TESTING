import json
import os
from datetime import datetime
from typing import List, Dict, Any

def save_requests(requests: List[Dict[str, Any]], filename: str = None) -> str:
    """Save generated requests to a JSON file with metadata"""
    
    # Create generated directory if it doesn't exist
    os.makedirs("generated", exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"requests_{timestamp}.json"
    
    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join("generated", filename)
    
    # Create output data with metadata
    output_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_requests": len(requests),
            "generation_stats": _get_request_stats(requests)
        },
        "requests": requests
    }
    
    # Save to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Generation Statistics:")
        _print_stats(output_data["metadata"]["generation_stats"])
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None

def load_requests(filepath: str) -> List[Dict[str, Any]]:
    """Load requests from a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old format (direct list) and new format (with metadata)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'requests' in data:
            return data['requests']
        else:
            print("❌ Invalid file format")
            return []
            
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in file: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return []

def _get_request_stats(requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics for generated requests"""
    if not requests:
        return {"total": 0}
    
    stats = {
        "total": len(requests),
        "methods": {},
        "has_headers": 0,
        "has_body": 0,
        "unique_urls": len(set(req.get('url', '') for req in requests)),
        "avg_headers_per_request": 0,
        "unique_domains": set()
    }
    
    total_headers = 0
    
    for request in requests:
        # Count methods
        method = request.get('method', 'UNKNOWN').upper()
        stats["methods"][method] = stats["methods"].get(method, 0) + 1
        
        # Count requests with headers/body
        headers = request.get('headers', {})
        if headers:
            stats["has_headers"] += 1
            total_headers += len(headers)
        
        if request.get('body') is not None:
            stats["has_body"] += 1
        
        # Extract domain from URL
        url = request.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                if domain:
                    stats["unique_domains"].add(domain)
            except:
                pass
    
    # Calculate averages
    if stats["has_headers"] > 0:
        stats["avg_headers_per_request"] = round(total_headers / stats["has_headers"], 2)
    
    # Convert set to count for JSON serialization
    stats["unique_domains"] = len(stats["unique_domains"])
    
    return stats

def _print_stats(stats: Dict[str, Any]):
    """Print formatted statistics"""
    print(f"  Total Requests: {stats.get('total', 0)}")
    
    methods = stats.get('methods', {})
    if methods:
        print(f"  HTTP Methods: {', '.join([f'{method}({count})' for method, count in methods.items()])}")
    
    print(f"  Unique URLs: {stats.get('unique_urls', 0)}")
    print(f"  Unique Domains: {stats.get('unique_domains', 0)}")
    print(f"  With Headers: {stats.get('has_headers', 0)}")
    print(f"  With Body: {stats.get('has_body', 0)}")
    
    if stats.get('avg_headers_per_request', 0) > 0:
        print(f"  Avg Headers per Request: {stats.get('avg_headers_per_request', 0)}")

def list_generated_files():
    """List all generated request files"""
    generated_dir = "generated"
    
    if not os.path.exists(generated_dir):
        print("📂 No generated files directory found")
        return []
    
    files = [f for f in os.listdir(generated_dir) if f.endswith('.json')]
    
    if not files:
        print("📂 No generated files found")
        return []
    
    print(f"📂 Found {len(files)} generated files:")
    for i, filename in enumerate(sorted(files), 1):
        filepath = os.path.join(generated_dir, filename)
        size = os.path.getsize(filepath)
        modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"  {i}. {filename} ({size} bytes, modified: {modified.strftime('%Y-%m-%d %H:%M')})")
    
    return files