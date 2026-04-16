#!/usr/bin/env python3
"""
QA Test Suite for Data Integrity
Tests that all associations have complete data and conflicts are properly tracked.

Issues Caught:
1. Data/Research Mismatch - Research found 3 conflicts but only 1 was in deployed data
2. Missing conflict fields - conflict_detected flag without required details
3. Orphan conflicts - Conflicts in DB not matching research findings
"""

import json
import sys
import os
from pathlib import Path

# Find project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_FILE = PROJECT_ROOT / "paris-assos-website" / "data_net.json"
RESEARCH_MANIFEST = PROJECT_ROOT / "FINAL_conflict_analysis.json"

def load_data():
    """Load deployed data from data_net.json"""
    if not DATA_FILE.exists():
        print(f"❌ CRITICAL: Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_research_manifest():
    """Load research manifest with conflict findings"""
    if not RESEARCH_MANIFEST.exists():
        print(f"⚠️  WARNING: Research manifest not found: {RESEARCH_MANIFEST}")
        return None
    
    with open(RESEARCH_MANIFEST, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_all_conflicts_have_required_fields():
    """
    Verify conflict associations have complete data.
    Each conflict must have: conflict_severity, conflict_details, board_members
    """
    print("\n[TEST] Checking all conflicts have required fields...")
    
    data = load_data()
    associations = data.get('associations', [])
    
    # Find all associations with conflict_detected flag
    conflicts = [a for a in associations if a.get('conflict_detected')]
    
    if not conflicts:
        print("ℹ️  No conflicts flagged in data (this may be OK if research is pending)")
        return True
    
    print(f"   Found {len(conflicts)} associations with conflict_detected flag")
    
    errors = []
    required_fields = ['conflict_severity', 'conflict_details', 'board_members']
    
    for assoc in conflicts:
        name = assoc.get('name', 'Unknown')
        siret = assoc.get('siret', 'No SIRET')
        
        for field in required_fields:
            if field not in assoc:
                errors.append(f"{name} ({siret}): missing '{field}'")
            elif field == 'conflict_severity' and not assoc[field]:
                errors.append(f"{name} ({siret}): '{field}' is empty")
            elif field == 'conflict_details' and not assoc[field]:
                errors.append(f"{name} ({siret}): '{field}' is empty")
            elif field == 'board_members':
                board = assoc.get('board_members', [])
                if not board or len(board) == 0:
                    errors.append(f"{name} ({siret}): no board_members data")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} conflicts missing required fields:")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
        return False
    
    print(f"✅ PASSED: All {len(conflicts)} conflicts have complete data")
    return True

def test_no_orphan_conflicts():
    """
    Verify all flagged conflicts exist in research DB.
    Cross-reference deployed conflicts with research findings.
    """
    print("\n[TEST] Checking for orphan conflicts (in data but not in research)...")
    
    data = load_data()
    manifest = load_research_manifest()
    
    if not manifest:
        print("ℹ️  SKIPPED: No research manifest available for cross-reference")
        return True
    
    associations = data.get('associations', [])
    conflicts_in_data = {a.get('siret') for a in associations if a.get('conflict_detected')}
    
    research_conflicts = set()
    for conflict in manifest.get('all_conflicts', []):
        research_conflicts.add(conflict.get('siret'))
    
    # Find conflicts in data but not in research (orphans)
    orphans = conflicts_in_data - research_conflicts
    
    # Find conflicts in research but not in data (missing from deployment)
    missing_from_data = research_conflicts - conflicts_in_data
    
    errors = []
    
    if orphans:
        errors.append(f"{len(orphans)} conflicts in data NOT in research manifest")
        for siret in list(orphans)[:5]:
            assoc = next((a for a in associations if a.get('siret') == siret), None)
            name = assoc.get('name', 'Unknown') if assoc else 'Unknown'
            errors.append(f"   Orphan: {name} ({siret})")
    
    if missing_from_data:
        errors.append(f"{len(missing_from_data)} conflicts in research NOT in data (deployment issue)")
        for siret in list(missing_from_data)[:5]:
            conflict = next((c for c in manifest.get('all_conflicts', []) if c.get('siret') == siret), None)
            name = conflict.get('association', 'Unknown') if conflict else 'Unknown'
            errors.append(f"   Missing: {name} ({siret})")
    
    if errors:
        print(f"❌ FAILED:")
        for err in errors[:12]:
            print(f"   {err}")
        return False
    
    print(f"✅ PASSED: No orphan conflicts")
    print(f"   - Conflicts in data: {len(conflicts_in_data)}")
    print(f"   - Conflicts in research: {len(research_conflicts)}")
    return True

def test_data_matches_research_manifest():
    """
    Verify deployed data matches research manifest.
    Compare conflict details between deployment and research.
    """
    print("\n[TEST] Checking deployed data matches research manifest...")
    
    data = load_data()
    manifest = load_research_manifest()
    
    if not manifest:
        print("ℹ️  SKIPPED: No research manifest available")
        return True
    
    associations = data.get('associations', [])
    conflicts_data = {a.get('siret'): a for a in associations if a.get('conflict_detected')}
    
    research_conflicts = {}
    for conflict in manifest.get('all_conflicts', []):
        research_conflicts[conflict.get('siret')] = conflict
    
    mismatches = []
    
    for siret, assoc in conflicts_data.items():
        if siret not in research_conflicts:
            continue  # Already caught in orphan test
        
        research = research_conflicts[siret]
        name = assoc.get('name', 'Unknown')
        
        # Check severity matches
        data_severity = assoc.get('conflict_severity', '').lower()
        research_severity = research.get('conflict_summary', {}).get('severity', '').lower()
        
        if data_severity != research_severity:
            mismatches.append(f"{name}: severity mismatch (data: {data_severity}, research: {research_severity})")
        
        # Check conflict count matches
        data_count = len(assoc.get('conflict_details', [])) if isinstance(assoc.get('conflict_details'), list) else 1
        research_count = research.get('conflict_summary', {}).get('total_conflicts', 0)
        
        if data_count != research_count:
            mismatches.append(f"{name}: conflict count mismatch (data: {data_count}, research: {research_count})")
    
    if mismatches:
        print(f"❌ FAILED: {len(mismatches)} mismatches between data and research:")
        for m in mismatches[:10]:
            print(f"   - {m}")
        return False
    
    print(f"✅ PASSED: Deployed data matches research manifest")
    return True

def test_all_conflicts_from_research_in_data():
    """
    CRITICAL: All conflicts identified by research MUST be in deployed data.
    This catches the issue where research found 3 conflicts but only 1 was deployed.
    """
    print("\n[TEST] Verifying ALL research conflicts are in deployed data...")
    
    data = load_data()
    manifest = load_research_manifest()
    
    if not manifest:
        print("ℹ️  SKIPPED: No research manifest available")
        return True
    
    research_conflicts = manifest.get('all_conflicts', [])
    associations = data.get('associations', [])
    
    missing = []
    
    for conflict in research_conflicts:
        siret = conflict.get('siret')
        name = conflict.get('association', 'Unknown')
        
        assoc_in_data = next((a for a in associations if a.get('siret') == siret), None)
        
        if not assoc_in_data:
            missing.append(f"{name} ({siret}): Association not found in data")
        elif not assoc_in_data.get('conflict_detected'):
            missing.append(f"{name} ({siret}): Association exists but conflict_detected=False")
    
    if missing:
        print(f"❌ FAILED: {len(missing)} research conflicts MISSING from deployed data:")
        for m in missing:
            print(f"   - {m}")
        print(f"\n🚨 This is the exact issue that slipped through!")
        print(f"   Research found {len(research_conflicts)} conflicts")
        print(f"   But only {len(research_conflicts) - len(missing)} are properly flagged in data")
        return False
    
    print(f"✅ PASSED: All {len(research_conflicts)} research conflicts are in deployed data")
    return True

def test_top_associations_have_complete_data():
    """Verify top 100 associations have all required display fields"""
    print("\n[TEST] Checking top 100 associations for complete data...")
    
    data = load_data()
    associations = sorted(
        data.get('associations', []),
        key=lambda x: x.get('netTotalAmount', 0),
        reverse=True
    )[:100]
    
    errors = []
    required_fields = ['name', 'siret', 'netTotalAmount', 'netYearlyData', 'netSubventions']
    
    for assoc in associations:
        name = assoc.get('name', 'Unknown')
        
        for field in required_fields:
            if field not in assoc:
                errors.append(f"{name}: missing '{field}'")
            elif field in ['netTotalAmount'] and assoc[field] is None:
                errors.append(f"{name}: '{field}' is None")
            elif field in ['netYearlyData', 'netSubventions'] and not assoc[field]:
                errors.append(f"{name}: '{field}' is empty")
    
    if errors:
        print(f"❌ FAILED: {len(errors)} issues in top 100:")
        for err in errors[:10]:
            print(f"   - {err}")
        return False
    
    print(f"✅ PASSED: All top 100 associations have complete data")
    return True

def run_all_tests():
    """Run all data integrity tests"""
    print("=" * 70)
    print("DATA INTEGRITY QA TESTS")
    print("=" * 70)
    print(f"Data file: {DATA_FILE}")
    print(f"Research manifest: {RESEARCH_MANIFEST}")
    
    results = []
    results.append(test_all_conflicts_have_required_fields())
    results.append(test_no_orphan_conflicts())
    results.append(test_data_matches_research_manifest())
    results.append(test_all_conflicts_from_research_in_data())
    results.append(test_top_associations_have_complete_data())
    
    print("\n" + "=" * 70)
    print("DATA INTEGRITY TEST SUMMARY")
    print("=" * 70)
    
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
