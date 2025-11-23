"""
Test script for all Product APIs
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api(name, url, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code < 400:
            print("[SUCCESS]")
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"Response: Array with {len(result)} items")
                    if len(result) > 0:
                        print(f"First item keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'N/A'}")
                elif isinstance(result, dict):
                    print(f"Response keys: {list(result.keys())}")
                    if 'success' in result:
                        print(f"Success: {result['success']}")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print("[FAILED]")
            print(f"Error: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("[CONNECTION ERROR] - Server might not be running")
    except requests.exceptions.Timeout:
        print("[TIMEOUT] - Request took too long - API might be hanging")
    except Exception as e:
        print(f"[ERROR]: {str(e)}")
    
    print()

# Test all Product APIs
print("="*60)
print("PRODUCT API TESTING")
print("="*60)

# 1. Get all products
test_api(
    "Get All Products",
    f"{BASE_URL}/api/products/"
)

# 2. Get products with empty params (the problematic one)
test_api(
    "Get Products with Empty Params",
    f"{BASE_URL}/api/products/?minPrice=&maxPrice=&page=1&limit=20"
)

# 3. Get products with filters
test_api(
    "Get Products with Filters",
    f"{BASE_URL}/api/products/?category=women&page=1&limit=5"
)

# 4. Get categories
test_api(
    "Get Categories",
    f"{BASE_URL}/api/products/categories/"
)

# 5. Get featured products
test_api(
    "Get Featured Products",
    f"{BASE_URL}/api/products/featured/"
)

# 6. Get trending products
test_api(
    "Get Trending Products",
    f"{BASE_URL}/api/products/trending/"
)

# 7. Get product detail (will need a valid product ID - testing with dummy)
test_api(
    "Get Product Detail (with dummy ID - will fail but test endpoint)",
    f"{BASE_URL}/api/products/507f1f77bcf86cd799439011/"
)

print("="*60)
print("TESTING COMPLETE")
print("="*60)

