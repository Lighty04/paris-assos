#!/usr/bin/env python3
"""
QA Test Suite for Frontend Display Validation

Simulates what the frontend displays to verify values can be shown.
This catches issues where the API returns data but the frontend
might not display it properly.

Problem Identified:
- API returns data ✅
- Frontend shows empty values ❌
- This test validates the data structure matches frontend expectations
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
    except Exception as e:
        return None

def format_currency(amount):
    """Format amount as currency (like frontend would)"""
    if amount is None:
        return "N/A"
    try:
        return f"{float(amount):,.0f} €"
    except (ValueError, TypeError):
        return str(amount)

def test_frontend_can_display_values():
    """
    Simulate what frontend displays.
    Verify values can be displayed (non-null, proper format).
    """
    print("\n[TEST 1] Simulating frontend display requirements...")
    
    data = make_api_request("/api/associations?page=1&per_page=50")
    if data is None:
        print("❌ FAILED: Could not connect to API")
        return False
    
    associations = data.get('associations', [])
    if not associations:
        print("❌ FAILED: No associations returned")
        return False
    
    print(f"   Testing {len(associations)} associations for display issues...")
    
    display_issues = []
    critical_issues = []
    
    for assoc in associations:
        name = assoc.get('name', 'Unknown')
        issues = []
        
        # Check netTotalAmount - this is displayed prominently
        net_total = assoc.get('netTotalAmount')
        if net_total is None:
            issues.append("netTotalAmount is None (will show empty)")
        elif net_total == 0:
            issues.append(f"netTotalAmount is zero (will show '0 €')")
        
        # Check last_year - displayed as "Year: XXXX"
        last_year = assoc.get('last_year')
        if last_year is None:
            issues.append("last_year is None (will show 'Year: -')")
        elif last_year == '':
            issues.append("last_year is empty string")
        
        # Check last_year_amount - displayed next to year
        last_year_amount = assoc.get('last_year_amount')
        if last_year_amount is None:
            issues.append("last_year_amount is None (will show empty)")
        elif last_year_amount == 0:
            # Zero might be valid if no subventions that year
            pass
        
        # Check name - critical for display
        if not assoc.get('name'):
            critical_issues.append(f"Association has no name - critical display issue")
        
        # Check sectors - displayed as tags
        sectors = assoc.get('sectors', [])
        if not sectors:
            issues.append("No sectors (tags will be empty)")
        
        # Check mission - displayed in detail view
        mission = assoc.get('mission', '')
        if not mission or mission == 'Non spécifié':
            issues.append("Mission not specified (will show placeholder)")
        
        # Check netYearlyData - used for graphs
        net_yearly = assoc.get('netYearlyData', {})
        if not net_yearly:
            issues.append("netYearlyData empty (graph will have no data)")
        else:
            # Check if any data points for graphs
            has_data = any(v and v > 0 for v in net_yearly.values())
            if not has_data:
                issues.append("netYearlyData has no non-zero values (graph flat)")
        
        # Check netSubventions - used for detailed view
        net_subventions = assoc.get('netSubventions', [])
        if not net_subventions:
            issues.append("netSubventions empty (detail view has no history)")
        
        if issues:
            display_issues.append({
                'name': name,
                'siret': assoc.get('siret', 'No SIRET'),
                'issues': issues
            })
    
    # Report findings
    if critical_issues:
        print(f"\n   ❌ CRITICAL ISSUES ({len(critical_issues)}):")
        for issue in critical_issues[:10]:
            print(f"     - {issue}")
    
    if display_issues:
        print(f"\n   ⚠️  Display Issues Found ({len(display_issues)}/{len(associations)} associations):")
        
        # Show top issues
        for item in display_issues[:10]:
            print(f"\n     {item['name']} ({item['siret'][:14]}...):")
            for issue in item['issues'][:5]:
                print(f"       - {issue}")
            if len(item['issues']) > 5:
                print(f"       ... and {len(item['issues']) - 5} more")
        
        if len(display_issues) > 10:
            print(f"\n     ... and {len(display_issues) - 10} more associations with issues")
    
    # Check if any associations have completely empty display values
    completely_empty = [
        item for item in display_issues
        if any("is None" in issue or "is zero" in issue for issue in item['issues'])
    ]
    
    if completely_empty:
        print(f"\n   🚨 CRITICAL: {len(completely_empty)} associations have empty critical values")
        print("      These would show blank/zero on the frontend!")
        for item in completely_empty[:5]:
            print(f"     - {item['name']}")
    
    # Summary
    print(f"\n   Summary:")
    print(f"   - Associations tested: {len(associations)}")
    print(f"   - With display issues: {len(display_issues)}")
    print(f"   - With critical empty values: {len(completely_empty)}")
    
    # Sample of good data
    good_data = [assoc for assoc in associations if assoc.get('name') 
                 and assoc.get('netTotalAmount') 
                 and assoc.get('last_year') is not None]
    print(f"   - Associations with complete data: {len(good_data)}")
    
    if good_data:
        sample = good_data[0]
        print(f"\n   ✅ Sample display (first complete association):")
        print(f"      Name: {sample.get('name')}")
        print(f"      Total: {format_currency(sample.get('netTotalAmount'))}")
        print(f"      Last Year: {sample.get('last_year')}")
        print(f"      Last Year Amount: {format_currency(sample.get('last_year_amount'))}")
    
    # Pass if most associations have displayable data
    if len(completely_empty) > len(associations) * 0.1:  # More than 10% empty
        print(f"\n❌ FAILED: {len(completely_empty)} associations have empty display values")
        return False
    else:
        print(f"\n✅ PASSED: Frontend can display values for most associations")
        return True

def test_frontend_detail_view():
    """
    Simulate detail view display requirements.
    """
    print("\n[TEST 2] Simulating detail view display...")
    
    # Get an association to test
    data = make_api_request("/api/associations?page=1&per_page=5")
    if not data or not data.get('associations'):
        print("❌ FAILED: Could not get test data")
        return False
    
    errors = []
    
    for assoc in data['associations'][:3]:  # Test first 3
        name = assoc.get('name', 'Unknown')
        
        # Check subventions list display
        subventions = assoc.get('subventions', [])
        if subventions:
            # Each subvention should have year, amount, object
            for i, sub in enumerate(subventions[:3]):  # Check first 3
                if not sub.get('year'):
                    errors.append(f"{name}: Subvention {i+1} missing year")
                if sub.get('amount') is None:
                    errors.append(f"{name}: Subvention {i+1} missing amount")
        
        # Check board members display
        board_members = assoc.get('board_members', [])
        # Board data is optional but if present should be displayable
        
        # Check graph data display
        net_yearly = assoc.get('netYearlyData', {})
        if net_yearly:
            years = sorted(net_yearly.keys())
            if len(years) < 2:
                errors.append(f"{name}: Graph has <2 data points")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} detail view issues")
        for err in errors[:10]:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: Detail view can display all data")
        return True

def test_frontend_card_display():
    """
    Test card component display (what users see in list view).
    """
    print("\n[TEST 3] Testing card component display...")
    
    data = make_api_request("/api/associations?page=1&per_page=20")
    if not data or not data.get('associations'):
        print("❌ FAILED: Could not get test data")
        return False
    
    # Card displays: name, total amount, sectors, last year info
    card_fields = ['name', 'netTotalAmount', 'sectors', 'last_year', 'siret']
    
    errors = []
    empty_cards = []
    
    for assoc in data['associations']:
        name = assoc.get('name', 'Unknown')
        
        # Check all card fields exist
        for field in card_fields:
            if field not in assoc:
                errors.append(f"{name}: Card missing '{field}'")
        
        # Check if card would be empty
        if not assoc.get('name') and not assoc.get('netTotalAmount'):
            empty_cards.append(name)
    
    if errors:
        print(f"❌ FAILED: {len(errors)} card display issues")
        for err in errors[:10]:
            print(f"   - {err}")
        return False
    
    if empty_cards:
        print(f"❌ FAILED: {len(empty_cards)} cards would be empty")
        return False
    
    print(f"✅ PASSED: All {len(data['associations'])} cards have displayable data")
    return True

def test_formatting_compatibility():
    """
    Test that values can be formatted like frontend does.
    """
    print("\n[TEST 4] Testing value formatting compatibility...")
    
    data = make_api_request("/api/associations?page=1&per_page=10")
    if not data or not data.get('associations'):
        print("❌ FAILED: Could not get test data")
        return False
    
    errors = []
    
    for assoc in data['associations']:
        # Test currency formatting
        net_total = assoc.get('netTotalAmount')
        if net_total is not None:
            try:
                formatted = format_currency(net_total)
            except Exception as e:
                errors.append(f"{assoc['name']}: Cannot format netTotalAmount: {e}")
        
        # Test year formatting
        last_year = assoc.get('last_year')
        if last_year is not None:
            try:
                year_str = str(int(last_year))
            except (ValueError, TypeError) as e:
                errors.append(f"{assoc['name']}: Cannot format last_year: {e}")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} formatting issues")
        for err in errors[:10]:
            print(f"   - {err}")
        return False
    
    print(f"✅ PASSED: All values can be formatted correctly")
    return True

def run_all_tests():
    """Run all frontend display tests"""
    print("=" * 60)
    print("FRONTEND DISPLAY QA TESTS")
    print("=" * 60)
    print("Simulating what the frontend displays to users")
    print(f"Testing API at: {API_BASE_URL}")
    
    results = []
    results.append(test_frontend_can_display_values())
    results.append(test_frontend_detail_view())
    results.append(test_frontend_card_display())
    results.append(test_formatting_compatibility())
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print("\n🎉 Frontend should display values correctly!")
        print("   All required fields are present and format properly.")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print("\n⚠️  Frontend display validation failed!")
        print("   Check API response and data integrity.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
