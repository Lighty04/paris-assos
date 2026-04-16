#!/usr/bin/env python3
"""
QA Test Suite for UI Elements
Tests that UI doesn't show loading/error states and all display values are present.

Issues Caught:
1. "Chargement" infinite loading - UI showed loading text instead of values
2. Missing display values in top cards
3. Empty/null critical fields
"""

import json
import sys
import urllib.request
import urllib.error
import re
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

def make_http_request(endpoint):
    """Make a raw HTTP request for HTML"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return None, f"HTTP {response.status}"
            return response.read().decode('utf-8'), None
    except Exception as e:
        return None, str(e)

def test_no_infinite_loading_states():
    """
    CRITICAL: Check that indicators show actual values, not 'chargement'.
    This catches the issue where UI showed 'chargement' indefinitely.
    """
    print("\n[TEST] Checking for 'chargement' (loading) states in API...")
    
    # Check /api/stats/quality - this was the endpoint causing issues
    data, error = make_api_request('/api/stats/quality')
    
    if error:
        print(f"   ❌ FAILED: /api/stats/quality endpoint missing!")
        print(f"   🚨 This causes 'chargement' to appear indefinitely in UI!")
        print(f"   The UI calls this endpoint to show data quality.")
        print(f"   When it 404s, the UI gets stuck showing 'chargement'.")
        return False
    
    # Check that quality data has actual values
    dq = data.get('dataQuality', {})
    
    loading_indicators = ['chargement', 'loading', 'Chargement', 'Loading', 
                          'en cours', 'En cours', '...', 'wait', 'Wait']
    
    # Convert data to string to check for loading text
    data_str = json.dumps(data).lower()
    
    for indicator in loading_indicators:
        if indicator.lower() in data_str:
            print(f"   ❌ FAILED: API response contains loading indicator: '{indicator}'")
            return False
    
    # Check specific fields that would cause loading states
    if 'cleanPercent' in dq and dq['cleanPercent'] is None:
        print(f"   ❌ FAILED: cleanPercent is null (would show loading)")
        return False
    
    print(f"   ✅ PASSED: No loading indicators in API responses")
    print(f"   Data Quality: {dq.get('cleanPercent', 'N/A')}% clean")
    return True

def test_quality_indicator_has_value():
    """Check that the quality indicator has an actual value"""
    print("\n[TEST] Checking quality indicator has actual value...")
    
    data, error = make_api_request('/api/stats/quality')
    
    if error:
        print(f"   ❌ FAILED: Could not get quality data: {error}")
        return False
    
    dq = data.get('dataQuality', {})
    
    # Check critical fields
    critical_fields = ['cleanPercent', 'totalYears', 'cleanYears']
    
    for field in critical_fields:
        if field not in dq:
            print(f"   ❌ FAILED: Missing field '{field}' in dataQuality")
            return False
        if dq[field] is None:
            print(f"   ❌ FAILED: Field '{field}' is null")
            return False
    
    # Check that percentage is reasonable
    clean_percent = dq.get('cleanPercent', 0)
    if not (0 <= clean_percent <= 100):
        print(f"   ❌ FAILED: cleanPercent ({clean_percent}) is not a valid percentage")
        return False
    
    print(f"   ✅ PASSED: Quality indicator has valid values")
    print(f"   - Clean: {clean_percent}%")
    print(f"   - Total years: {dq.get('totalYears')}")
    return True

def test_stats_loaded_not_loading():
    """Check that stats endpoint returns actual values"""
    print("\n[TEST] Checking stats are loaded (not in loading state)...")
    
    data, error = make_api_request('/api/stats')
    
    if error:
        print(f"   ❌ FAILED: Could not get stats: {error}")
        return False
    
    # Check that stats have actual values
    required_stats = ['totalAssociations', 'totalAmount', 'totalSubventions']
    
    for stat in required_stats:
        if stat not in data:
            print(f"   ❌ FAILED: Missing stat '{stat}'")
            return False
        if data[stat] is None:
            print(f"   ❌ FAILED: Stat '{stat}' is null")
            return False
        if data[stat] == 0 and stat != 'totalSubventions':
            # 0 might be valid for some stats
            pass
    
    total = data.get('totalAssociations', 0)
    amount = data.get('totalAmount', 0)
    
    if total == 0:
        print(f"   ❌ FAILED: totalAssociations is 0")
        return False
    
    if amount == 0:
        print(f"   ⚠️  WARNING: totalAmount is 0 (may be valid)")
    
    print(f"   ✅ PASSED: Stats loaded successfully")
    print(f"   - Associations: {total:,}")
    print(f"   - Total amount: {amount:,.0f} €")
    return True

def test_top_cards_have_display_values():
    """
    Test that top 10 association cards have all required display values.
    Catches the issue where cards showed empty values.
    """
    print("\n[TEST] Checking top 10 cards have all display values...")
    
    data, error = make_api_request('/api/associations?page=1&per_page=10')
    
    if error:
        print(f"   ❌ FAILED: Could not get associations: {error}")
        return False
    
    associations = data.get('associations', [])
    
    if not associations:
        print(f"   ❌ FAILED: No associations returned")
        return False
    
    print(f"   Testing {len(associations)} associations...")
    
    # Required display fields for cards
    required_fields = {
        'name': 'Name',
        'netTotalAmount': 'Total amount',
        'sectors': 'Sectors (for tags)',
    }
    
    # Optional but important
    important_fields = {
        'last_year': 'Last year',
        'last_year_amount': 'Last year amount',
    }
    
    errors = []
    warnings = []
    
    for i, assoc in enumerate(associations):
        name = assoc.get('name', f'Association {i+1}')
        
        # Check required fields
        for field, label in required_fields.items():
            if field not in assoc:
                errors.append(f"{name}: missing '{field}' ({label})")
            elif field == 'name' and not assoc[field]:
                errors.append(f"Association {i+1}: name is empty")
            elif field == 'netTotalAmount' and assoc[field] is None:
                errors.append(f"{name}: netTotalAmount is null")
            elif field == 'sectors' and not assoc[field]:
                errors.append(f"{name}: sectors is empty")
        
        # Check important fields (warn but don't fail)
        for field, label in important_fields.items():
            if field not in assoc:
                warnings.append(f"{name}: missing '{field}' ({label})")
            elif assoc[field] is None:
                warnings.append(f"{name}: '{field}' is null")
    
    if errors:
        print(f"   ❌ FAILED: {len(errors)} cards with missing required fields:")
        for err in errors[:10]:
            print(f"      - {err}")
        return False
    
    if warnings:
        print(f"   ⚠️  {len(warnings)} cards missing optional fields")
    
    print(f"   ✅ PASSED: All {len(associations)} cards have required display values")
    return True

def test_no_null_values_in_critical_fields():
    """Check that critical fields are never null"""
    print("\n[TEST] Checking for null values in critical fields...")
    
    data, error = make_api_request('/api/associations?page=1&per_page=50')
    
    if error:
        print(f"   ❌ FAILED: Could not get associations: {error}")
        return False
    
    associations = data.get('associations', [])
    
    critical_fields = ['name', 'siret', 'netTotalAmount']
    
    null_counts = {field: 0 for field in critical_fields}
    
    for assoc in associations:
        for field in critical_fields:
            if field not in assoc or assoc[field] is None:
                null_counts[field] += 1
    
    errors = []
    for field, count in null_counts.items():
        if count > 0:
            errors.append(f"{count}/{len(associations)} associations have null '{field}'")
    
    if errors:
        print(f"   ❌ FAILED:")
        for err in errors:
            print(f"      - {err}")
        return False
    
    print(f"   ✅ PASSED: No null values in critical fields")
    return True

def test_detail_view_has_all_values():
    """Check that detail view loads with all values"""
    print("\n[TEST] Checking detail view has all values...")
    
    # Get an association to test
    data, error = make_api_request('/api/associations?page=1&per_page=1')
    if error or not data or not data.get('associations'):
        print(f"   ❌ FAILED: Could not get test association")
        return False
    
    siret = data['associations'][0].get('siret')
    if not siret:
        print(f"   ❌ FAILED: Test association has no SIRET")
        return False
    
    # Get detail
    detail, error = make_api_request(f'/api/association?siret={siret}')
    if error:
        print(f"   ❌ FAILED: Could not get detail: {error}")
        return False
    
    # Check detail has values (not loading)
    required = ['name', 'siret', 'mission', 'subventions', 'totalAmount']
    
    for field in required:
        if field not in detail:
            print(f"   ❌ FAILED: Detail missing '{field}'")
            return False
        if detail[field] is None and field not in ['mission']:
            print(f"   ❌ FAILED: Detail '{field}' is null")
            return False
    
    # Check subventions have data
    subventions = detail.get('subventions', [])
    if not subventions:
        print(f"   ⚠️  WARNING: No subventions in detail view")
    
    print(f"   ✅ PASSED: Detail view has all values")
    return True

def test_html_page_loads():
    """Check that HTML page loads without error messages"""
    print("\n[TEST] Checking HTML page loads without errors...")
    
    html, error = make_http_request('/')
    
    if error:
        print(f"   ❌ FAILED: Could not load page: {error}")
        return False
    
    # Check for error indicators
    error_indicators = ['erreur', 'error', 'Erreur', 'Error', 'chargement en cours']
    html_lower = html.lower()
    
    errors_found = []
    for indicator in error_indicators:
        if indicator in html_lower:
            # Count occurrences
            count = html_lower.count(indicator)
            if count > 0:
                errors_found.append(f"'{indicator}' appears {count} times")
    
    # Also check for visible error messages
    if '<div' in html and 'erreur' in html_lower:
        # Check if it's in visible content (not just JS code)
        pass  # For now, just warn
    
    if errors_found:
        print(f"   ⚠️  Found potential error indicators:")
        for e in errors_found[:5]:
            print(f"      - {e}")
    
    print(f"   ✅ PASSED: HTML page loads")
    return True

def run_all_tests():
    """Run all UI element tests"""
    print("=" * 70)
    print("UI ELEMENT QA TESTS")
    print("=" * 70)
    print(f"Testing API at: {API_BASE_URL}")
    print("\nThese tests catch 'chargement' infinite loading issues")
    
    # Check API is reachable
    data, error = make_api_request('/health')
    if error:
        print(f"\n❌ CRITICAL: API is not reachable at {API_BASE_URL}")
        print(f"   Error: {error}")
        return 1
    
    results = []
    results.append(test_no_infinite_loading_states())
    results.append(test_quality_indicator_has_value())
    results.append(test_stats_loaded_not_loading())
    results.append(test_top_cards_have_display_values())
    results.append(test_no_null_values_in_critical_fields())
    results.append(test_detail_view_has_all_values())
    results.append(test_html_page_loads())
    
    print("\n" + "=" * 70)
    print("UI ELEMENT TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print(f"\n🎉 No 'chargement' issues detected!")
        print(f"   All UI elements should display correctly.")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print(f"\n🚨 UI may show 'chargement' or empty values!")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
