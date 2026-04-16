#!/usr/bin/env python3
"""
Pre-deployment and post-deployment tests for paris-assos-website
"""

import os
import sys
import subprocess
import json

def test_index_html_exists():
    """Verify index.html exists in local workspace"""
    local_path = "/home/openclaw/.openclaw/workspace/paris-assos-website/index.html"
    assert os.path.exists(local_path), f"index.html not found at {local_path}"
    size = os.path.getsize(local_path)
    assert size > 80000, f"index.html seems too small ({size} bytes)"
    print(f"✅ index.html exists ({size} bytes)")
    return True

def test_data_net_json_exists():
    """Verify data_net.json exists and is valid JSON"""
    data_path = "/home/openclaw/.openclaw/workspace/paris-assos-website/data_net.json"
    assert os.path.exists(data_path), f"data_net.json not found at {data_path}"
    
    with open(data_path) as f:
        data = json.load(f)
    
    assert 'associations' in data, "data_net.json missing 'associations' key"
    assert len(data['associations']) > 0, "data_net.json has no associations"
    print(f"✅ data_net.json valid ({len(data['associations'])} associations)")
    return True

def test_remote_index_html_exists():
    """Verify index.html exists on remote server"""
    remote_path = "/home/decisionhelper/website/index.html"
    result = subprocess.run(
        ["ssh", "decisionhelper@192.168.0.16", f"ls -la {remote_path}"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"index.html not found on remote: {result.stderr}"
    print(f"✅ Remote index.html exists")
    return True

def test_remote_data_exists():
    """Verify data_net.json exists on remote server"""
    remote_path = "/home/decisionhelper/website/data_net.json"
    result = subprocess.run(
        ["ssh", "decisionhelper@192.168.0.16", f"ls -la {remote_path}"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"data_net.json not found on remote: {result.stderr}"
    print(f"✅ Remote data_net.json exists")
    return True

def test_website_accessible():
    """Verify website responds with 200"""
    import urllib.request
    try:
        response = urllib.request.urlopen("http://192.168.0.16:8010/")
        assert response.getcode() == 200, f"Website returned {response.getcode()}"
        print(f"✅ Website accessible (HTTP 200)")
        return True
    except Exception as e:
        raise AssertionError(f"Website not accessible: {e}")

def run_all_tests():
    """Run all deployment tests"""
    tests = [
        ("Local index.html exists", test_index_html_exists),
        ("Local data_net.json valid", test_data_net_json_exists),
        ("Remote index.html exists", test_remote_index_html_exists),
        ("Remote data_net.json exists", test_remote_data_exists),
        ("Website accessible", test_website_accessible),
    ]
    
    print("=" * 50)
    print("Deployment Tests")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name}: Unexpected error: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
