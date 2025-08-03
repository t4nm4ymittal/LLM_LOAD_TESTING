import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Tuple

class EndpointParser:
    """Smart parser for extracting path variables and query parameters from endpoints"""
    
    @staticmethod
    def parse_endpoint(endpoint: str) -> Tuple[str, List[str], Dict[str, str]]:
        """
        Parse endpoint to extract base path, path variables, and query parameters
        
        Args:
            endpoint: Full endpoint string (e.g., "/users/{userId}/posts?limit=10&sort=date")
            
        Returns:
            Tuple of (clean_path, path_variables, query_parameters)
        """
        # Parse URL to separate path and query
        parsed = urlparse(endpoint)
        path = parsed.path
        query = parsed.query
        
        # Extract path variables
        path_vars = EndpointParser.extract_path_variables(path)
        
        # Extract query parameters
        query_params = EndpointParser.extract_query_parameters(query)
        
        return path, path_vars, query_params
    
    @staticmethod
    def extract_path_variables(path: str) -> List[str]:
        """Extract path variables from path string"""
        # Find all {variable} patterns
        path_vars = re.findall(r'\{([^}]+)\}', path)
        return path_vars
    
    @staticmethod
    def extract_query_parameters(query_string: str) -> Dict[str, str]:
        """Extract query parameters from query string"""
        if not query_string:
            return {}
        
        query_dict = parse_qs(query_string, keep_blank_values=True)
        # Convert list values to single values (parse_qs returns lists)
        return {k: v[0] if v else '' for k, v in query_dict.items()}
    
    @staticmethod
    def build_sample_url(base_url: str, endpoint: str, path_vars: Dict[str, str], 
                        query_params: Dict[str, str]) -> str:
        """Build a complete sample URL with provided values"""
        # Start with base URL and endpoint
        full_url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        
        # Replace path variables
        for var_name, var_value in path_vars.items():
            full_url = full_url.replace(f'{{{var_name}}}', str(var_value))
        
        # Add query parameters
        if query_params:
            # Remove existing query string first
            if '?' in full_url:
                full_url = full_url.split('?')[0]
            
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            full_url += f"?{query_string}"
        
        return full_url
    
    @staticmethod
    def validate_endpoint(endpoint: str) -> Tuple[bool, str]:
        """Validate endpoint format and return any issues"""
        issues = []
        
        # Check for unmatched braces
        open_braces = endpoint.count('{')
        close_braces = endpoint.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
        
        # Check for empty path variables
        empty_vars = re.findall(r'\{\s*\}', endpoint)
        if empty_vars:
            issues.append("Found empty path variables: {}")
        
        # Check for nested braces
        nested = re.findall(r'\{[^}]*\{|\}[^{]*\}', endpoint)
        if nested:
            issues.append("Found nested or malformed braces")
        
        # Check for valid path variable names
        path_vars = re.findall(r'\{([^}]+)\}', endpoint)
        for var in path_vars:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var.strip()):
                issues.append(f"Invalid path variable name: '{var}' (use letters, numbers, underscore)")
        
        is_valid = len(issues) == 0
        error_msg = "; ".join(issues) if issues else ""
        
        return is_valid, error_msg
