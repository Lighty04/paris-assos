"""QA Test: Verify website is properly deployed and reachable"""

import urllib.request
import sys
import json

BASE_URL = "http://localhost:8010"

def test_server_reachable():
    """Test 1: Server responds to health check"""
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/health", timeout=10)
        assert response.status == 200
        data = json.loads(response.read())
        assert data.get('status') == 'healthy'
        print("✅ Server reachable and healthy")
        return True
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False

def test_api_responds():
    """Test 2: API endpoints return data"""
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/api/stats", timeout=10)
        assert response.status == 200
        data = json.loads(response.read())
        assert data.get('totalAmount', 0) > 0
        print(f"✅ API responds (total: {data.get('totalAmount')})")
        return True
    except Exception as e:
        print(f"❌ API not responding: {e}")
        return False

def test_homepage_loads():
    """Test 3: Homepage loads"""
    try:
        response = urllib.request.urlopen(BASE_URL, timeout=10)
        assert response.status == 200
        html = response.read().decode()
        assert 'Paris' in html or 'subvention' in html.lower()
        print("✅ Homepage loads")
        return True
    except Exception as e:
        print(f"❌ Homepage not loading: {e}")
        return False

def test_associations_endpoint():
    """Test 4: Associations API returns data"""
    try:
        response = urllib.request.urlopen(
            f"{BASE_URL}/api/associations?page=1&per_page=10", timeout=10)
        assert response.status == 200
        data = json.loads(response.read())
        assert len(data.get('associations', [])) > 0
        print(f"✅ Associations API returns {len(data.get('associations', []))} records")
        return True
    except Exception as e:
        print(f"❌ Associations API failed: {e}")
        return False

def test_required_fields_present():
    """Test 5: API returns required fields (catches missing last_year)"""
    try:
        response = urllib.request.urlopen(
            f"{BASE_URL}/api/associations?page=1&per_page=1", timeout=10)
        data = json.loads(response.read())
        assoc = data['associations'][0]
        
        required = ['netTotalAmount', 'last_year', 'last_year_amount', 'name', 'siret']
        missing = [f for f in required if f not in assoc]
        
        if missing:
            print(f"❌ Missing fields: {missing}")
            return False
        print(f"✅ All required fields present")
        return True
    except Exception as e:
        print(f"❌ Field check failed: {e}")
        return False

if __name__ == '__main__':
    tests = [
        test_server_reachable,
        test_api_responds,
        test_homepage_loads,
        test_associations_endpoint,
        test_required_fields_present
    ]
    
    results = [t() for t in tests]
    passed = sum(results)
    
    print(f"\n{'='*50}")
    print(f"Deployment Tests: {passed}/{len(results)} passed")
    print(f"{'='*50}")
    
    sys.exit(0 if all(results) else 1)
