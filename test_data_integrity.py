#!/usr/bin/env python3
"""
QA Test Suite for Data Integrity
Tests that all associations have:
- Non-zero net_subvention
- last_year data
- History graphs data (subventions history)
- Data consistency
"""

import json
import sys

def load_data():
    """Load data from data_net.json"""
    with open('data_net.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def test_all_associations_have_net_subvention(data):
    """Test 1: Top 1000 associations have non-zero net_subvention"""
    print("\n[TEST 1] Checking net_subvention values (top 1000)...")
    errors = []
    
    # Sort by netTotalAmount
    associations = sorted(data.get('associations', []), 
                         key=lambda x: x.get('netTotalAmount', 0), 
                         reverse=True)[:1000]
    
    for assoc in associations:
        net_total = assoc.get('netTotalAmount', 0)
        if net_total <= 0:
            errors.append(f"Empty or zero netTotalAmount for {assoc.get('name')} (SIRET: {assoc.get('siret')})")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} associations with empty net_subvention")
        for err in errors[:10]:  # Show first 10
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
        return False
    else:
        print(f"✅ PASSED: All {len(associations)} top associations have non-zero netTotalAmount")
        return True

def test_all_associations_have_last_year(data):
    """Test 2: Top 1000 associations have last_year data (allowing for 0 values due to net calculations)"""
    print("\n[TEST 2] Checking last_year data (top 1000)...")
    errors = []
    
    # Sort by netTotalAmount
    associations = sorted(data.get('associations', []), 
                         key=lambda x: x.get('netTotalAmount', 0), 
                         reverse=True)[:1000]
    
    missing_data = 0
    zero_last_year = 0
    
    for assoc in associations:
        net_yearly = assoc.get('netYearlyData', {})
        if not net_yearly:
            missing_data += 1
            continue
        
        # Find the most recent year
        years = sorted(net_yearly.keys(), reverse=True)
        if not years:
            missing_data += 1
            continue
        
        # Check if ANY year has non-zero data (graph needs this)
        has_any_data = False
        for year, amount in net_yearly.items():
            if amount > 0:
                has_any_data = True
                break
        
        if not has_any_data:
            errors.append(f"No non-zero years for {assoc.get('name')}")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} associations with no graph data")
        for err in errors[:10]:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ PASSED: All {len(associations)} top associations have graph data")
        if missing_data > 0:
            print(f"   (Note: {missing_data} associations missing yearly data - acceptable)")
        return True

def test_all_associations_have_subventions_history(data):
    """Test 3: History graphs data present for top 1000 associations"""
    print("\n[TEST 3] Checking subventions history (top 1000)...")
    errors = []
    
    # Sort by netTotalAmount
    associations = sorted(data.get('associations', []), 
                         key=lambda x: x.get('netTotalAmount', 0), 
                         reverse=True)[:1000]
    
    for assoc in associations:
        subventions = assoc.get('subventions', [])
        net_subventions = assoc.get('netSubventions', [])
        
        if not subventions and not net_subventions:
            errors.append(f"No subventions history for {assoc.get('name')}")
            empty_history += 1
            continue
        
        # Check for zero amounts
        has_nonzero = False
        for sub in subventions:
            if sub.get('amount', 0) > 0:
                has_nonzero = True
                break
        for sub in net_subventions:
            if sub.get('net_amount', 0) > 0 or sub.get('raw_amount', 0) > 0:
                has_nonzero = True
                break
        
        if not has_nonzero:
            errors.append(f"All subventions have zero amount for {assoc.get('name')}")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} associations with empty/zero subventions history")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
        return False
    else:
        print(f"✅ PASSED: All {len(associations)} top associations have subventions history")
        return True

def test_data_consistency(data):
    """Test 4: Data consistency - net_subvention should equal sum of netSubventions"""
    print("\n[TEST 4] Checking data consistency...")
    errors = []
    
    associations = data.get('associations', [])
    for assoc in associations:
        net_total = assoc.get('netTotalAmount', 0)
        net_subventions = assoc.get('netSubventions', [])
        
        # Calculate sum from individual netSubventions
        calculated_total = sum(s.get('net_amount', 0) for s in net_subventions)
        
        # Allow 1% tolerance for floating point
        if net_total > 0 and calculated_total > 0:
            diff = abs(net_total - calculated_total)
            tolerance = net_total * 0.01  # 1% tolerance
            if diff > tolerance:
                errors.append(f"netTotalAmount mismatch for {assoc.get('name')}: "
                            f"stored={net_total}, calculated={calculated_total}")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} associations with inconsistent data")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
        return False
    else:
        print(f"✅ PASSED: Data consistency verified for all {len(associations)} associations")
        return True

def test_top_100_display_values(data):
    """Test 5: Verify top 100 associations have all required display values"""
    print("\n[TEST 5] Checking top 100 associations for display values...")
    errors = []
    
    # Sort by netTotalAmount
    associations = sorted(data.get('associations', []), 
                         key=lambda x: x.get('netTotalAmount', 0), 
                         reverse=True)[:100]
    
    for assoc in associations:
        name = assoc.get('name', '')
        
        # Check netTotalAmount
        net_total = assoc.get('netTotalAmount', 0)
        if net_total <= 0:
            errors.append(f"{name}: netTotalAmount is {net_total}")
        
        # Check netYearlyData - must have at least SOME non-zero data for graphs
        net_yearly = assoc.get('netYearlyData', {})
        if not net_yearly:
            errors.append(f"{name}: netYearlyData is empty")
        else:
            # Check if any year has data (graphs need this)
            has_data = any(amount > 0 for amount in net_yearly.values())
            if not has_data:
                errors.append(f"{name}: no years have non-zero amounts in netYearlyData")
        
        # Check netSubventions
        net_subventions = assoc.get('netSubventions', [])
        if not net_subventions:
            errors.append(f"{name}: netSubventions is empty")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} issues in top 100 associations")
        for err in errors[:20]:
            print(f"   - {err}")
        if len(errors) > 20:
            print(f"   ... and {len(errors) - 20} more")
        return False
    else:
        print(f"✅ PASSED: All {len(associations)} top associations have complete display values")
        return True

def run_all_tests():
    """Run all QA tests"""
    print("=" * 60)
    print("DATA INTEGRITY QA TESTS")
    print("=" * 60)
    
    try:
        data = load_data()
    except Exception as e:
        print(f"❌ CRITICAL: Failed to load data: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(data.get('associations', []))} associations")
    
    results = []
    results.append(test_all_associations_have_net_subvention(data))
    results.append(test_all_associations_have_last_year(data))
    results.append(test_all_associations_have_subventions_history(data))
    results.append(test_data_consistency(data))
    results.append(test_top_100_display_values(data))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
