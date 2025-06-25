#!/usr/bin/env python3
"""
API Test Script for TogoMedium SPARQLIST
Tests all API endpoints by parsing MD files in the repository directory.
"""

import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import glob
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Default base URL
DEFAULT_BASE_URL = 'http://localhost:3000'

# Special default values for specific endpoints
SPECIAL_DEFAULTS = {
    'gmdb_taxonomy_search_by_name': {'q': 'Nocardioides'},
    'gmdb_taxonomy_gtdb_search_by_name': {'q': 'Nocardioides'}
}

# Endpoints to exclude from testing
EXCLUDED_ENDPOINTS = {
    'gms_kegg_code_tid',
    'gms_by_kegg_tids_3'
}

def parse_md_file(file_path: str) -> Dict[str, Any]:
    """Parse MD file to extract API endpoint name and parameters."""
    endpoint_name = os.path.basename(file_path).replace('.md', '')
    parameters = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Parameters section
    param_section = re.search(r'## Parameters\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if param_section:
        param_text = param_section.group(1)
        
        # Parse parameters with their default values
        param_matches = re.findall(r'\* `([^`]+)`[^\n]*\n(?:\s*\* default: ([^\n]+))?', param_text)
        
        for param_name, default_value in param_matches:
            parameters[param_name] = default_value.strip() if default_value else None
    
    return {
        'endpoint': endpoint_name,
        'parameters': parameters
    }

def build_api_url(base_url: str, endpoint: str, parameters: Dict[str, Optional[str]]) -> str:
    """Build API URL with parameters."""
    url = f"{base_url}/sparqlist/api/{endpoint}"
    
    # Add parameters with default values
    query_params = {}
    for param_name, default_value in parameters.items():
        if default_value is not None:
            query_params[param_name] = default_value
    
    # Add special default values for specific endpoints
    if endpoint in SPECIAL_DEFAULTS:
        for param_name, special_value in SPECIAL_DEFAULTS[endpoint].items():
            query_params[param_name] = special_value
    
    if query_params:
        url += "?" + urllib.parse.urlencode(query_params)
    
    return url

def analyze_json_response(data: Any) -> Dict[str, Any]:
    """Analyze JSON response and return structure information."""
    if isinstance(data, list):
        analysis = {
            'type': 'array',
            'count': len(data)
        }
        # Check if array contains objects or simple values
        if data and isinstance(data[0], dict):
            analysis['first_item_keys'] = list(data[0].keys())
            analysis['array_type'] = 'objects'
        else:
            analysis['array_type'] = 'simple_values'
        return analysis
    elif isinstance(data, dict):
        analysis = {
            'type': 'object',
            'keys': list(data.keys())
        }
        # Check if 'total' key exists and add its value
        if 'total' in data:
            analysis['total'] = data['total']
        return analysis
    else:
        return {
            'type': type(data).__name__,
            'value': str(data)[:100] + '...' if len(str(data)) > 100 else str(data)
        }

def test_api_endpoint(base_url: str, endpoint_info: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single API endpoint."""
    endpoint = endpoint_info['endpoint']
    parameters = endpoint_info['parameters']
    
    url = build_api_url(base_url, endpoint, parameters)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')
            
        # Parse JSON response
        try:
            json_data = json.loads(content)
            analysis = analyze_json_response(json_data)
            
            return {
                'endpoint': endpoint,
                'url': url,
                'status': 'success',
                'response_analysis': analysis
            }
        except json.JSONDecodeError as e:
            return {
                'endpoint': endpoint,
                'url': url,
                'status': 'json_error',
                'error': f"JSON decode error: {str(e)}",
                'raw_content': content[:200] + '...' if len(content) > 200 else content
            }
            
    except urllib.error.HTTPError as e:
        return {
            'endpoint': endpoint,
            'url': url,
            'status': 'http_error',
            'error': f"HTTP {e.code}: {e.reason}"
        }
    except urllib.error.URLError as e:
        return {
            'endpoint': endpoint,
            'url': url,
            'status': 'connection_error',
            'error': f"Connection error: {str(e)}"
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'url': url,
            'status': 'error',
            'error': f"Unexpected error: {str(e)}"
        }

def main():
    """Main function to run API tests."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = DEFAULT_BASE_URL
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    # Generate log filename with timestamp  
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Extract hostname for log filename
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(base_url)
        hostname = parsed_url.hostname or 'localhost'
        port = f"_{parsed_url.port}" if parsed_url.port else ""
        log_prefix = f"{hostname}{port}"
    except:
        log_prefix = "api_test"
    
    log_filename = f"{log_prefix}_{timestamp}.log"
    log_path = os.path.join(os.path.dirname(__file__), log_filename)
    
    # Start logging and console output
    def log_and_print(message: str, log_file):
        print(message)
        log_file.write(message + "\n")
        log_file.flush()
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_and_print(f"Testing API endpoints: {base_url}", log_file)
        log_and_print("=" * 60, log_file)
        
        # Find all MD files in repository directory
        repo_dir = os.path.join(os.path.dirname(__file__), '..', 'repository')
        md_files = glob.glob(os.path.join(repo_dir, '*.md'))
        
        if not md_files:
            log_and_print("No MD files found in repository directory", log_file)
            sys.exit(1)
        
        results = []
        total_files = len(md_files)
        
        for i, md_file in enumerate(md_files, 1):
            endpoint_name = os.path.basename(md_file).replace('.md', '')
            
            # Skip excluded endpoints
            if endpoint_name in EXCLUDED_ENDPOINTS:
                log_and_print(f"[{i}/{total_files}] Skipping {os.path.basename(md_file)} (excluded)", log_file)
                continue
                
            log_and_print(f"[{i}/{total_files}] Testing {os.path.basename(md_file)}...", log_file)
            
            try:
                endpoint_info = parse_md_file(md_file)
                result = test_api_endpoint(base_url, endpoint_info)
                results.append(result)
                
                # Print result summary
                if result['status'] == 'success':
                    analysis = result['response_analysis']
                    if analysis['type'] == 'array':
                        if analysis['array_type'] == 'objects':
                            log_and_print(f"  ✓ Success: Array with {analysis['count']} items", log_file)
                            if analysis.get('first_item_keys'):
                                log_and_print(f"    First item keys: {', '.join(analysis['first_item_keys'])}", log_file)
                        else:
                            log_and_print(f"  ✓ Success: Simple array with {analysis['count']} items", log_file)
                    elif analysis['type'] == 'object':
                        total_info = f" (total: {analysis['total']})" if 'total' in analysis else ""
                        log_and_print(f"  ✓ Success: Object with keys: {', '.join(analysis['keys'])}{total_info}", log_file)
                    else:
                        log_and_print(f"  ✓ Success: {analysis['type']} - {analysis.get('value', '')}", log_file)
                else:
                    log_and_print(f"  ✗ Failed: {result['error']}", log_file)
                    
            except Exception as e:
                log_and_print(f"  ✗ Error parsing file: {str(e)}", log_file)
                results.append({
                    'endpoint': os.path.basename(md_file).replace('.md', ''),
                    'status': 'parse_error',
                    'error': str(e)
                })
        
        # Summary
        log_and_print("\n" + "=" * 60, log_file)
        log_and_print("SUMMARY", log_file)
        log_and_print("=" * 60, log_file)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        log_and_print(f"Total endpoints tested: {total_count}", log_file)
        log_and_print(f"Successful: {success_count}", log_file)
        log_and_print(f"Failed: {total_count - success_count}", log_file)
        
        if total_count - success_count > 0:
            log_and_print("\nFailed endpoints:", log_file)
            for result in results:
                if result['status'] != 'success':
                    log_and_print(f"  - {result['endpoint']}: {result['error']}", log_file)
        
        # Write detailed results to log
        log_file.write("\n" + "=" * 60 + "\n")
        log_file.write("DETAILED RESULTS\n")
        log_file.write("=" * 60 + "\n")
        
        for result in results:
            log_file.write(f"\nEndpoint: {result['endpoint']}\n")
            log_file.write(f"Status: {result['status']}\n")
            log_file.write(f"URL: {result.get('url', 'N/A')}\n")
            
            if result['status'] == 'success':
                analysis = result['response_analysis']
                log_file.write(f"Response Type: {analysis['type']}\n")
                if analysis['type'] == 'array':
                    log_file.write(f"Item Count: {analysis['count']}\n")
                    if analysis['array_type'] == 'objects' and analysis.get('first_item_keys'):
                        log_file.write(f"First Item Keys: {', '.join(analysis['first_item_keys'])}\n")
                    log_file.write(f"Array Type: {analysis['array_type']}\n")
                elif analysis['type'] == 'object':
                    log_file.write(f"Object Keys: {', '.join(analysis['keys'])}\n")
                    if 'total' in analysis:
                        log_file.write(f"Total: {analysis['total']}\n")
                else:
                    log_file.write(f"Value: {analysis.get('value', '')}\n")
            else:
                log_file.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
            log_file.write("-" * 40 + "\n")
        
        log_and_print(f"\nResults saved to: {log_path}", log_file)

if __name__ == '__main__':
    main()