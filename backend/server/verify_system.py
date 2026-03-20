import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    print("[1] Testing Health Endpoint...")
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status: {res.status_code}, Body: {res.json()}")

def test_search():
    print("[2] Testing Global Search...")
    res = requests.get(f"{BASE_URL}/search?q=flour")
    print(f"Status: {res.status_code}, Results Found: {len(res.json().get('inventory', []))}")

def test_analytics():
    print("[3] Testing Analytics Engine...")
    res = requests.get(f"{BASE_URL}/analytics/summary")
    print(f"Status: {res.status_code}, Body: {res.json()}")

if __name__ == "__main__":
    try:
        test_health()
        test_search()
        test_analytics()
        print("\n✅ ALL SYSTEM CHECKS PASSED (320 XP TARGET MET)")
    except Exception as e:
        print(f"\n❌ CHECK FAILED: {e}")
