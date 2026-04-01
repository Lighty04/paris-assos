#!/usr/bin/env python3
"""
QA Test Suite for API Response Validation
Tests that the actual API returns all required fields frontend needs.
This is CRITICAL - we need to test the API response, not just the data file!

Problem Identified:
- Data file had last_year fields ✅
- API wasn't returning last_year fields ❌
- Tests passed but frontend showed empty values

These tests catch the disconnect between data and API.
"""

import json
import sys
import urllib.request
import urllib.error

API_BASE_URL = "http://localhost:8010"

def make_api_request(endpoint):
    """Make an API request and return JSON response"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        resp = urllib.request.urlopen(url, timeout=10).read().decode()
        return json.loads(resp)
    except urllib.error.URLError as e:
        print(f"❌ API connection failed: {e}")
        print(f"   Is the server running at {API_BASE_URL}?")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response from API: {e}")
        return None
    except Exception as e:
        print(f"❌ API request error: {e}")
        return None

def test_api_returns_all_required_fields():
    """Test that /api/associations returns all fields frontend needs"""
    print("\n[TEST 1] Checking API returns all required fields...")
    
    # Required fields that frontend expects
    required_fields = [
        'name',
        'siret',
        'mission',
        'sectors',
        'subventions',
        'totalAmount',
        'board_members',
        'netTotalAmount',       # CRITICAL - for display
        'netSubventions',       # CRITICAL - for calculations
        'netYearlyData',        # CRITICAL - for graphs
        'last_year',           # CRITICAL - was missing!
        'last_year_amount',    # CRITICAL - was missing!
    ]
    
    # Non-null fields - these must have actual values
    non_null_fields = [
        'netTotalAmount',
        'last_year_amount',
        'name',
    ]
    
    data = make_api_request("/api/associations?page=1&per_page=50")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    associations = data.get('associations', [])
    if not associations:
        print("❌ FAILED: No associations returned from API")
        return False
    
    print(f"   Testing {len(associations)} associations from API...")
    
    errors = []
    missing_field_counts = {field: 0 for field in required_fields}
    null_field_counts = {field: 0 for field in non_null_fields}
    
    for assoc in associations:
        name = assoc.get('name', 'Unknown')
        
        # Check all required fields exist
        for field in required_fields:
            if field not in assoc:
                missing_field_counts[field] += 1
                if missing_field_counts[field] <= 5:  # Limit error messages
                    errors.append(f"{name}: API missing field '{field}'")
        
        # Check non-null fields have values
        for field in non_null_fields:
            if field in assoc and assoc[field] is None:
                null_field_counts[field] += 1
                if null_field_counts[field] <= 5:
                    errors.append(f"{name}: Field '{field}' is None")
            elif field in assoc and field in ['netTotalAmount', 'last_year_amount']:
                if assoc[field] == 0 or assoc[field] == '':
                    null_field_counts[field] += 1
                    if null_field_counts[field] <= 5:
                        errors.append(f"{name}: Field '{field}' is empty/zero")
    
    # Summary of missing fields
    total_missing = sum(missing_field_counts.values())
    total_null = sum(null_field_counts.values())
    
    if total_missing > 0:
        print(f"\n   Missing field summary:")
        for field, count in missing_field_counts.items():
            if count > 0:
                print(f"     - '{field}': missing in {count}/{len(associations)} associations")
    
    if total_null > 0:
        print(f"\n   Null/empty field summary:")
        for field, count in null_field_counts.items():
            if count > 0:
                print(f"     - '{field}': null/empty in {count}/{len(associations)} associations")
    
    if errors:
        print(f"\n   First errors (showing up to 10):")
        for err in errors[:10]:
            print(f"     - {err}")
        return False
    else:
        print(f"✅ PASSED: All {len(associations)} associations have required fields")
        print(f"   - Required fields present: {len(required_fields)}")
        print(f"   - Non-null fields validated: {len(non_null_fields)}")
        return True

def test_api_stats_endpoint():
    """Test /api/stats returns data"""
    print("\n[TEST 2] Checking /api/stats endpoint...")
    
    data = make_api_request("/api/stats")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    required_stats = ['totalAssociations', 'totalAmount', 'totalSubventions', 'yearRange']
    errors = []
    
    for field in required_stats:
        if field not in data:
            errors.append(f"Missing stat field: '{field}'")
    
    # Check totalAmount is valid
    if 'totalAmount' in data:
        if data['totalAmount'] is None or data['totalAmount'] == 0:
            errors.append("totalAmount is None or zero")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} issues with stats endpoint")
        for err in errors[:5]:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: /api/stats returns valid data")
        print(f"   - Total associations: {data.get('totalAssociations')}")
        print(f"   - Total amount: {data.get('totalAmount'):,.0f}")
        return True

def test_api_detail_endpoint():
    """Test /api/association detail endpoint returns all fields"""
    print("\n[TEST 3] Checking /api/association detail endpoint...")
    
    # First get an association to test with
    list_data = make_api_request("/api/associations?page=1&per_page=1")
    if list_data is None or not list_data.get('associations'):
        print("❌ FAILED: Could not get test association")
        return False
    
    test_siret = list_data['associations'][0].get('siret')
    if not test_siret:
        print("❌ FAILED: Test association has no SIRET")
        return False
    
    detail_data = make_api_request(f"/api/association?siret={test_siret}")
    if detail_data is None:
        print("❌ FAILED: Could not fetch association detail")
        return False
    
    # Check detail has all the same fields as list
    required_fields = [
        'name', 'siret', 'mission', 'sectors', 'subventions',
        'totalAmount', 'netTotalAmount', 'netSubventions', 'netYearlyData',
        'last_year', 'last_year_amount'
    ]
    
    errors = []
    for field in required_fields:
        if field not in detail_data:
            errors.append(f"Detail endpoint missing field: '{field}'")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} issues with detail endpoint")
        for err in errors[:5]:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: /api/association detail returns all fields")
        return True

def test_api_pagination():
    """Test pagination works correctly"""
    print("\n[TEST 4] Checking API pagination...")
    
    data = make_api_request("/api/associations?page=1&per_page=10")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    # Check pagination object
    pagination = data.get('pagination', {})
    required_pagination = ['page', 'per_page', 'total', 'total_pages']
    
    errors = []
    for field in required_pagination:
        if field not in pagination:
            errors.append(f"Missing pagination field: '{field}'")
    
    # Check associations array
    associations = data.get('associations', [])
    if not associations:
        errors.append("No associations in paginated response")
    
    # Should return exactly 10 per_page requested
    if len(associations) != min(10, pagination.get('total', 0)):
        if pagination.get('total', 0) >= 10:
            errors.append(f"Expected 10 associations, got {len(associations)}")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} pagination issues")
        for err in errors[:5]:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: Pagination working correctly")
        print(f"   - Page: {pagination.get('page')}")
        print(f"   - Per page: {pagination.get('per_page')}")
        print(f"   - Total: {pagination.get('total')}")
        return True

def test_api_filters_endpoint():
    """Test /api/filters returns filter options"""
    print("\n[TEST 5] Checking /api/filters endpoint...")
    
    data = make_api_request("/api/filters")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    errors = []
    
    if 'years' not in data:
        errors.append("Missing 'years' in filters")
    elif not isinstance(data['years'], list):
        errors.append("'years' is not a list")
    
    if 'sectors' not in data:
        errors.append("Missing 'sectors' in filters")
    elif not isinstance(data['sectors'], list):
        errors.append("'sectors' is not a list")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} issues with filters endpoint")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: /api/filters returns valid data")
        print(f"   - Years: {len(data.get('years', []))} unique years")
        print(f"   - Sectors: {len(data.get('sectors', []))} unique sectors")
        return True

def test_api_health_endpoint():
    """Test health check endpoint"""
    print("\n[TEST 6] Checking /health endpoint...")
    
    data = make_api_request("/health")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    if data.get('status') != 'healthy':
        print(f"❌ FAILED: Health check returned status: {data.get('status')}")
        return False
    
    if 'associations_count' not in data:
        print("❌ FAILED: Health check missing associations_count")
        return False
    
    print(f"✅ PASSED: Health check healthy")
    print(f"   - Associations: {data.get('associations_count')}")
    print(f"   - Cache status: {data.get('cache_status')}")
    return True

def run_all_tests():
    """Run all API response tests"""
    print("=" * 60)
    print("API RESPONSE QA TESTS")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    
    results = []
    results.append(test_api_health_endpoint())
    results.append(test_api_returns_all_required_fields())
    results.append(test_api_stats_endpoint())
    results.append(test_api_detail_endpoint())
    results.append(test_api_pagination())
    results.append(test_api_filters_endpoint())
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print("\n🎉 The API is returning all required fields!")
        print("   Frontend should display values correctly.")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print("\n⚠️  API response validation failed!")
        print("   This would have caught the missing last_year fields issue.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
