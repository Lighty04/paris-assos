# QA Tests for Paris Subventions Project

Comprehensive QA test suite to catch deployment issues BEFORE release.

## Purpose

These tests catch the issues that previously slipped through:

1. **Data/Research Mismatch** - Research found 3 conflicts, only 1 was deployed
2. **Missing API Endpoint** - `/api/stats/quality` didn't exist → UI showed "chargement" forever  
3. **Filter/Display Logic Mismatch** - Filter expected conflict data format, data had different structure

## Quick Start

```bash
cd qa_tests
python3 run_all_qa_tests.py
```

With custom API URL:
```bash
python3 run_all_qa_tests.py --api-url http://localhost:8000
```

## Test Modules

### 1. test_deployment_integrity.py
Verifies workspace matches deployment and Git state is clean.

**Catches:**
- Uncommitted changes in critical files
- Corrupted or truncated data files
- Missing deployment files
- Duplicate SIRETs in data

### 2. test_data_integrity.py
Verifies data consistency and conflict detection alignment with research.

**Catches:**
- Conflicts missing from deployed data (the 3 conflicts issue!)
- Orphan conflicts (in data but not in research)
- Missing conflict fields (severity, details, board_members)
- Top associations missing display values

### 3. test_api_endpoints.py
Verifies ALL UI dependency endpoints exist and return valid data.

**Catches:**
- Missing `/api/stats/quality` endpoint (causes "chargement")
- Missing required fields in API responses
- API errors and slow responses
- CORS issues

### 4. test_filter_functionality.py
Verifies all filters work correctly and return expected counts.

**Catches:**
- Year filter returning wrong results
- Sector filter not working
- Search returning incorrect matches
- Combined filters breaking
- Stats not respecting filter params

### 5. test_ui_elements.py
Verifies UI doesn't show loading/error states.

**Catches:**
- "Chargement" infinite loading (missing quality endpoint)
- Null values in display fields
- Missing card data (name, amount, etc.)
- Detail view empty values
- HTML error messages

## Command Line Options

```bash
# Run all tests
python3 run_all_qa_tests.py

# Test against specific API URL
python3 run_all_qa_tests.py --api-url http://localhost:8000

# Skip specific tests
python3 run_all_qa_tests.py --skip api filter ui

# Run only specific tests
python3 run_all_qa_tests.py --only data deployment
```

## Exit Codes

- `0` - All tests passed, deployment is safe
- `1` - Some tests failed, fix issues before deploying

## Integration with HEARTBEAT.md

The HEARTBEAT.md has been updated with:
- Pre-deployment QA checklist
- Mandatory test run requirement
- Troubleshooting guide

## Test Output

When tests pass:
```
✅ ALL TESTS PASSED: 5/5

🎉 ALL TESTS PASSED!
You can proceed with deployment.
```

When tests fail:
```
❌ SOME TESTS FAILED!

Please fix the issues above before deploying.
Common fixes:
  - Missing API endpoint: Add the endpoint to server.py
  - Data mismatch: Sync research findings to data file
  - Loading states: Check API responses have actual values
```

## Adding New Tests

To add a new test:

1. Create `test_new_feature.py` in the `qa_tests/` directory
2. Follow the pattern of existing tests:
   - Import required modules
   - Define test functions that return True/False
   - Use `print()` for progress and results
   - Create `run_all_tests()` function
3. Add the test to `TEST_MODULES` in `run_all_qa_tests.py`
4. Update this README

## Example Test Structure

```python
def test_feature_works():
    print("\n[TEST] Testing feature...")
    
    # Your test logic here
    if something_wrong:
        print("❌ FAILED: explanation")
        return False
    
    print("✅ PASSED: feature works")
    return True

def run_all_tests():
    print("=" * 70)
    print("FEATURE QA TESTS")
    print("=" * 70)
    
    results = []
    results.append(test_feature_works())
    
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
```

## Success Criteria

Before deployment, ALL of the following must be true:

- [ ] `python3 run_all_qa_tests.py` returns exit code 0
- [ ] All 5 test suites pass
- [ ] No "chargement" or loading states detected
- [ ] All filters return expected counts
- [ ] Workspace files match deployment
- [ ] All research conflicts are in deployed data

## Known Limitations

1. API tests require the server to be running
2. Some tests may produce false warnings if data is being actively modified
3. Git tests may be skipped if Git is not available

## Maintenance

Update tests when:
- New API endpoints are added
- Data structure changes
- New filters or UI elements are introduced
- Research methodology changes

---

*Last updated: QA test suite created to prevent deployment issues*
