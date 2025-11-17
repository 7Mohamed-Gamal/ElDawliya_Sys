import requests

# Test without following redirects
url = "http://localhost:8000/api/v1/auth/token/"
headers = {"Content-Type": "application/json"}

# Try different username variations
test_credentials = [
    {"username": "admin", "password": "hgslduhgfwdv"},
    {"username": "Admin", "password": "hgslduhgfwdv"},
    {"username": "ADMIN", "password": "hgslduhgfwdv"},
]

for creds in test_credentials:
    print(f"\n=== Testing with username: {creds['username']} ===")
    try:
        response = requests.post(url, json=creds, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ SUCCESS! Response: {response.json()}")
            break
        else:
            print(f"❌ FAILED. Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

