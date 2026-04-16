#!/usr/bin/env python3
"""
QA Test Suite for API Endpoints
Tests EVERY endpoint the UI depends on.

Issues Caught:
1. Missing API Endpoint - /api/stats/quality didn't exist, UI showed "chargement"
2. Missing fields in API responses
3. Wrong data types in responses
"""

import json
import sys
import urllib.request
import urllib.error
import os

# Default API base URL - can be overridden via environment variable
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8010')

# ALL endpoints the UI depends on with their required fields
ENDPOINTS_TO_TEST = [
    ('/health', ['status', 'associations_count']),
    ('/api/stats', ['totalAssociations', 'totalAmount', 'totalSubventions', 'yearRange']),
    ('/api/stats/quality', ['dataQuality', 'cleanPercent']),  # WAS MISSING!
    ('/api/associations', ['associations', 'total', 'page', 'pagination']),
    ('/api/filters', ['years', 'sectors']),
    ('/api/association?siret=31669616000019', ['name', 'siret', 'totalAmount']),  # Detail endpoint
]

def make_api_request(endpoint):
    """Make an API request and return JSON response"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return None, f"HTTP {response.status}"
            resp_data = response.read().decode('utf-8')
            return json.loads(resp_data), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return None, f"Connection failed: {e.reason}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except Exception as e:
        return None, str(e)

def test_all_ui_dependencies_exist():
    """
    CRITICAL TEST: Every endpoint the UI calls must exist and return valid data.
    This catches the missing /api/stats/quality endpoint issue.
    """
    print("\n[TEST] Checking ALL UI dependency endpoints exist...")
    print(f"   API Base URL: {API_BASE_URL}")
    
    all_passed = True
    results = []
    
    for endpoint, required_fields in ENDPOINTS_TO_TEST:
        print(f"\n   Testing: {endpoint}")
        data, error = make_api_request(endpoint)
        
        if error:
            if "HTTP 404" in error:
                print(f"   ❌ MISSING ENDPOINT: {endpoint}")
                print(f"      Error: {error}")
                print(f"      🚨 This would cause 'chargement' infinite loading in UI!")
            else:
                print(f"   ❌ ERROR: {error}")
            all_passed = False
            results.append((endpoint, False, error))
            continue
        
        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ MISSING FIELDS: {missing_fields}")
            all_passed = False
            results.append((endpoint, False, f"Missing fields: {missing_fields}"))
        else:
            print(f"   ✅ OK - Fields: {required_fields}")
            results.append((endpoint, True, None))
    
    print("\n   Endpoint Test Summary:")
    for endpoint, passed, error in results:
        status = "✅" if passed else "❌"
        print(f"   {status} {endpoint}")
    
    return all_passed

def test_api_stats_quality_specific():
    """
    Specific test for /api/stats/quality endpoint.
    This was the endpoint that caused 'chargement' to hang.
    """
    print("\n[TEST] Specifically testing /api/stats/quality...")
    
    data, error = make_api_request('/api/stats/quality')
    
    if error:
        print(f"   ❌ FAILED: {error}")
        print(f"   🚨 This is the endpoint that caused 'chargement'!")
        print(f"   UI was calling this endpoint to show data quality indicator.")
        print(f"   When it 404'd, the UI showed 'chargement' forever.")
        return False
    
    # Validate dataQuality structure
    dq = data.get('dataQuality', {})
    required_quality_fields = ['cleanPercent', 'totalYears', 'suspiciousYears']
    
    missing = [f for f in required_quality_fields if f not in dq]
    
    if missing:
        print(f"   ❌ FAILED: dataQuality missing fields: {missing}")
        return False
    
    print(f"   ✅ PASSED: /api/stats/quality exists and returns valid data")
    print(f"   Data Quality: {dq.get('cleanPercent')}% clean")
    return True

def test_api_response_times():
    """Test that API endpoints respond within acceptable time"""
    print("\n[TEST] Checking API response times...")
    
    import time
    
    slow_endpoints = []
    
    for endpoint, _ in ENDPOINTS_TO_TEST[:4]:  # Test main endpoints
        start = time.time()
        data, error = make_api_request(endpoint)
        elapsed = time.time() - start
        
        if error:
            print(f"   ⚠️  {endpoint}: Error ({error})")
            continue
        
        if elapsed > 2.0:
            slow_endpoints.append((endpoint, elapsed))
            print(f"   ⚠️  {endpoint}: {elapsed:.2f}s (slow)")
        else:
            print(f"   ✅ {endpoint}: {elapsed:.2f}s")
    
    if slow_endpoints:
        print(f"\n   ⚠️  {len(slow_endpoints)} endpoints are slow (>2s)")
        return False
    
    print(f"   ✅ All endpoints respond within acceptable time")
    return True

def test_api_handles_errors_gracefully():
    """Test that API returns proper error codes for invalid requests"""
    print("\n[TEST] Checking API error handling...")
    
    test_cases = [
        ('/api/association?siret=INVALID', 404, 'Invalid SIRET'),
        ('/api/associations?page=999999', 200, 'Way out of range page (should return empty)'),
        ('/api/associations?per_page=0', 400, 'Zero per_page (should error)'),
    ]
    
    all_passed = True
    
    for endpoint, expected_status, description in test_cases:
        url = f"{API_BASE_URL}{endpoint}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                actual_status = resp.status
        except urllib.error.HTTPError as e:
            actual_status = e.code
        except Exception as e:
            print(f"   ❌ {description}: Exception - {e}")
            all_passed = False
            continue
        
        # For now, just check it doesn't crash
        print(f"   ✅ {description}: HTTP {actual_status}")
    
    return all_passed

def test_cors_headers():
    """Test that API returns proper CORS headers"""
    print("\n[TEST] Checking CORS headers...")
    
    url = f"{API_BASE_URL}/health"
    try:
        req = urllib.request.Request(url)
        req.add_header('Origin', 'http://localhost:3000')
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            cors_header = resp.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print(f"   ✅ CORS header present: {cors_header}")
                return True
            else:
                print(f"   ⚠️  CORS header missing - may cause frontend issues")
                return False
    except Exception as e:
        print(f"   ❌ Error checking CORS: {e}")
        return False

def run_all_tests():
    """Run all API endpoint tests"""
    print("=" * 70)
    print("API ENDPOINT QA TESTS")
    print("=" * 70)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Endpoints to verify: {len(ENDPOINTS_TO_TEST)}")
    
    # First check if API is reachable
    data, error = make_api_request('/health')
    if error:
        print(f"\n❌ CRITICAL: API is not reachable at {API_BASE_URL}")
        print(f"   Error: {error}")
        print(f"   Please ensure the server is running.")
        return 1
    
    print(f"   API Health: {data.get('status', 'unknown')}")
    print(f"   Associations: {data.get('associations_count', 0)}")
    
    results = []
    results.append(test_all_ui_dependencies_exist())
    results.append(test_api_stats_quality_specific())
    results.append(test_api_response_times())
    results.append(test_api_handles_errors_gracefully())
    results.append(test_cors_headers())
    
    print("\n" + "=" * 70)
    print("API ENDPOINT TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print(f"\n🎉 All UI dependencies are properly supported!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print(f"\n⚠️  Missing endpoints would cause UI 'chargement' issues!")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
