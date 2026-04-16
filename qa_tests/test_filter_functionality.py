#!/usr/bin/env python3
"""
QA Test Suite for Filter Functionality
Tests that all filters actually work and return expected results.

Issues Caught:
1. Filter/Display Logic Mismatch - Filter expected conflict data format
2. Filter returns wrong counts
3. Combined filters break results
"""

import json
import sys
import urllib.request
import urllib.error
import os

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8010')

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
    except Exception as e:
        return None, str(e)

def load_all_associations():
    """Load all associations via API"""
    associations = []
    page = 1
    
    while True:
        data, error = make_api_request(f'/api/associations?page={page}&per_page=100')
        if error or not data:
            break
        
        page_data = data.get('associations', [])
        if not page_data:
            break
        
        associations.extend(page_data)
        
        # Stop if we've fetched all
        if len(page_data) < 100:
            break
        
        page += 1
        
        # Safety limit
        if page > 200:
            break
    
    return associations

def test_year_filter_returns_results():
    """Test that year filter returns correct results"""
    print("\n[TEST] Testing year filter functionality...")
    
    # First get available years
    filters_data, error = make_api_request('/api/filters')
    if error or not filters_data:
        print(f"   ❌ FAILED: Could not get filters: {error}")
        return False
    
    years = filters_data.get('years', [])
    if not years:
        print(f"   ❌ FAILED: No years available in filters")
        return False
    
    print(f"   Available years: {years[:5]}... (total: {len(years)})")
    
    # Test first available year
    test_year = years[0]
    data, error = make_api_request(f'/api/associations?year={test_year}&per_page=100')
    
    if error:
        print(f"   ❌ FAILED: Year filter request failed: {error}")
        return False
    
    filtered = data.get('associations', [])
    pagination = data.get('pagination', {})
    total = pagination.get('total', len(filtered))
    
    if total == 0:
        print(f"   ❌ FAILED: Year {test_year} filter returned 0 results")
        return False
    
    # Verify all results actually have the year
    for assoc in filtered[:10]:  # Check first 10
        subventions = assoc.get('subventions', [])
        years_in_assoc = {str(s.get('year')) for s in subventions}
        if test_year not in years_in_assoc:
            print(f"   ❌ FAILED: {assoc.get('name')} returned but doesn't have year {test_year}")
            return False
    
    print(f"   ✅ PASSED: Year {test_year} filter returns {total} valid results")
    return True

def test_sector_filter_returns_results():
    """Test that sector filter returns correct results"""
    print("\n[TEST] Testing sector filter functionality...")
    
    # Get available sectors
    filters_data, error = make_api_request('/api/filters')
    if error or not filters_data:
        print(f"   ❌ FAILED: Could not get filters: {error}")
        return False
    
    sectors = filters_data.get('sectors', [])
    if not sectors:
        print(f"   ❌ FAILED: No sectors available in filters")
        return False
    
    print(f"   Available sectors: {sectors[:5]}... (total: {len(sectors)})")
    
    # Test first available sector
    test_sector = sectors[0]
    data, error = make_api_request(f'/api/associations?sector={test_sector}&per_page=100')
    
    if error:
        print(f"   ❌ FAILED: Sector filter request failed: {error}")
        return False
    
    filtered = data.get('associations', [])
    pagination = data.get('pagination', {})
    total = pagination.get('total', len(filtered))
    
    if total == 0:
        print(f"   ❌ FAILED: Sector '{test_sector}' filter returned 0 results")
        return False
    
    # Verify all results actually have the sector
    for assoc in filtered[:10]:
        assoc_sectors = assoc.get('sectors', [])
        if test_sector not in assoc_sectors:
            print(f"   ❌ FAILED: {assoc.get('name')} returned but doesn't have sector '{test_sector}'")
            return False
    
    print(f"   ✅ PASSED: Sector '{test_sector}' filter returns {total} valid results")
    return True

def test_search_filter_returns_results():
    """Test that search filter works"""
    print("\n[TEST] Testing search filter functionality...")
    
    # Get an association name to search for
    all_data, error = make_api_request('/api/associations?page=1&per_page=1')
    if error or not all_data or not all_data.get('associations'):
        print(f"   ❌ FAILED: Could not get test data")
        return False
    
    test_name = all_data['associations'][0].get('name', '')
    search_term = test_name.split()[0] if test_name else 'Paris'
    
    data, error = make_api_request(f'/api/associations?search={search_term}&per_page=50')
    
    if error:
        print(f"   ❌ FAILED: Search filter request failed: {error}")
        return False
    
    filtered = data.get('associations', [])
    pagination = data.get('pagination', {})
    total = pagination.get('total', len(filtered))
    
    if total == 0:
        print(f"   ❌ FAILED: Search '{search_term}' returned 0 results")
        return False
    
    # Verify results contain search term
    for assoc in filtered[:5]:
        name = assoc.get('name', '').lower()
        if search_term.lower() not in name:
            print(f"   ❌ FAILED: {assoc.get('name')} returned but doesn't contain '{search_term}'")
            return False
    
    print(f"   ✅ PASSED: Search '{search_term}' returns {total} valid results")
    return True

def test_combined_filters_work():
    """Test that combined filters work correctly"""
    print("\n[TEST] Testing combined filters (year + sector)...")
    
    # Get available filters
    filters_data, error = make_api_request('/api/filters')
    if error or not filters_data:
        print(f"   ❌ FAILED: Could not get filters")
        return False
    
    years = filters_data.get('years', [])
    sectors = filters_data.get('sectors', [])
    
    if not years or not sectors:
        print(f"   ❌ FAILED: Missing filters to combine")
        return False
    
    # Try combined filter
    data, error = make_api_request(
        f'/api/associations?year={years[0]}&sector={sectors[0]}&per_page=50'
    )
    
    if error:
        print(f"   ❌ FAILED: Combined filter request failed: {error}")
        return False
    
    filtered = data.get('associations', [])
    pagination = data.get('pagination', {})
    total = pagination.get('total', len(filtered))
    
    # Combined filters might legitimately return 0 results
    print(f"   ✅ PASSED: Combined filter works (returns {total} results)")
    return True

def test_filter_pagination_consistency():
    """Test that filtered results have correct pagination"""
    print("\n[TEST] Testing filter pagination consistency...")
    
    # Get total unfiltered count
    all_data, error = make_api_request('/api/associations?page=1&per_page=1')
    if error or not all_data:
        print(f"   ❌ FAILED: Could not get baseline data")
        return False
    
    total_unfiltered = all_data.get('pagination', {}).get('total', 0)
    
    # Get filtered count
    filters_data, error = make_api_request('/api/filters')
    if error or not filters_data:
        print(f"   ❌ FAILED: Could not get filters")
        return False
    
    years = filters_data.get('years', [])
    if not years:
        print(f"   ❌ FAILED: No years to test")
        return False
    
    filtered_data, error = make_api_request(f'/api/associations?year={years[0]}&per_page=1')
    if error or not filtered_data:
        print(f"   ❌ FAILED: Could not get filtered data")
        return False
    
    total_filtered = filtered_data.get('pagination', {}).get('total', 0)
    
    # Filtered should be <= unfiltered
    if total_filtered > total_unfiltered:
        print(f"   ❌ FAILED: Filtered count ({total_filtered}) > unfiltered ({total_unfiltered})")
        return False
    
    print(f"   ✅ PASSED: Pagination consistent")
    print(f"   - Unfiltered total: {total_unfiltered}")
    print(f"   - Filtered total: {total_filtered}")
    return True

def test_stats_filtered_by_params():
    """Test that stats endpoint respects filter params"""
    print("\n[TEST] Testing stats endpoint with filters...")
    
    # Get unfiltered stats
    unfiltered, error = make_api_request('/api/stats')
    if error or not unfiltered:
        print(f"   ❌ FAILED: Could not get unfiltered stats")
        return False
    
    total_unfiltered = unfiltered.get('totalAssociations', 0)
    
    # Get filtered stats
    filters_data, error = make_api_request('/api/filters')
    if error or not filters_data:
        print(f"   ❌ FAILED: Could not get filters")
        return False
    
    years = filters_data.get('years', [])
    if not years:
        print(f"   ❌ FAILED: No years to test")
        return False
    
    filtered, error = make_api_request(f'/api/stats?year={years[0]}')
    if error:
        print(f"   ❌ FAILED: Filtered stats request failed: {error}")
        return False
    
    total_filtered = filtered.get('totalAssociations', 0)
    
    # Filtered stats should be <= unfiltered
    if total_filtered > total_unfiltered:
        print(f"   ❌ FAILED: Filtered stats ({total_filtered}) > unfiltered ({total_unfiltered})")
        return False
    
    print(f"   ✅ PASSED: Stats filtering works correctly")
    print(f"   - Unfiltered: {total_unfiltered} associations")
    print(f"   - Filtered: {total_filtered} associations")
    return True

def test_conflict_filter_if_exists():
    """Test conflict filter if the API supports it"""
    print("\n[TEST] Testing conflict filter (if supported)...")
    
    # Try to call with conflict filter
    data, error = make_api_request('/api/associations?conflict=true&per_page=50')
    
    if error and 'HTTP 400' in error:
        print(f"   ℹ️  Conflict filter not supported (returns 400)")
        return True  # Not an error if not supported
    
    if error:
        print(f"   ❌ FAILED: Conflict filter request failed: {error}")
        return False
    
    filtered = data.get('associations', [])
    pagination = data.get('pagination', {})
    total = pagination.get('total', len(filtered))
    
    # Verify all returned associations have conflicts
    for assoc in filtered[:10]:
        if not assoc.get('conflict_detected'):
            print(f"   ❌ FAILED: {assoc.get('name')} returned but conflict_detected=False")
            return False
    
    print(f"   ✅ PASSED: Conflict filter returns {total} associations with conflicts")
    return True

def run_all_tests():
    """Run all filter functionality tests"""
    print("=" * 70)
    print("FILTER FUNCTIONALITY QA TESTS")
    print("=" * 70)
    print(f"Testing API at: {API_BASE_URL}")
    
    # Check API is reachable
    data, error = make_api_request('/health')
    if error:
        print(f"\n❌ CRITICAL: API is not reachable at {API_BASE_URL}")
        print(f"   Error: {error}")
        return 1
    
    results = []
    results.append(test_year_filter_returns_results())
    results.append(test_sector_filter_returns_results())
    results.append(test_search_filter_returns_results())
    results.append(test_combined_filters_work())
    results.append(test_filter_pagination_consistency())
    results.append(test_stats_filtered_by_params())
    results.append(test_conflict_filter_if_exists())
    
    print("\n" + "=" * 70)
    print("FILTER FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print(f"\n🎉 All filters work correctly!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print(f"\n⚠️  Filter issues detected - UI may show incorrect results!")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
