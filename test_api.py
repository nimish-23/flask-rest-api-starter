import requests
import json
import time

print("=" * 60)
print("FLASK REST API - REFACTOR VERIFICATION")
print("=" * 60)

BASE_URL = "http://127.0.0.1:5000"
TIMESTAMP = int(time.time())
USERNAME = f"u{TIMESTAMP}"[-8:] # Short unique username (8 chars)
EMAIL = f"user_{TIMESTAMP}@example.com"
PASSWORD = "password123"

# Test 1: Registration (Auth Route)
print(f"\n1️⃣  Testing Registration ({EMAIL})...")
url = f"{BASE_URL}/auth/register"
data = {
    "username": USERNAME,
    "email": EMAIL,
    "password": PASSWORD
}

response = requests.post(url, json=data)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

if response.status_code != 201:
    print("❌ Registration failed! Aborting.")
    exit(1)

# Test 2: Login (Auth Route)
print(f"\n2️⃣  Testing Login...")
url = f"{BASE_URL}/auth/login"
login_data = {
    "email": EMAIL,
    "password": PASSWORD
}

response = requests.post(url, json=login_data)
print(f"   Status: {response.status_code}")
result = response.json()

if response.status_code != 200:
    print("❌ Login failed! Aborting.")
    exit(1)

access_token = result.get('access_token')
print(f"   Access Token: {access_token[:20]}...")

# Test 3: Get Me (Users Route)
# Note: This is now under /users/me or /auth/me depends on registration
# In __init__.py we registered users_bp with prefix /users
print("\n3️⃣  Testing Get Me (/users/me)...")
url = f"{BASE_URL}/users/me"
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(url, headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

if response.status_code == 200:
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Refactor Successful.")
    print("=" * 60)
else:
    print(f"\n❌ Get Me failed with status {response.status_code}")
