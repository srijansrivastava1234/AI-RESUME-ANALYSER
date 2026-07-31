import urllib.request
import json
import sys

URL = "http://127.0.0.1:8000/"

print("Running local backend connectivity check...")

try:
    with urllib.request.urlopen(URL, timeout=3) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print("SUCCESS: Backend is online and responsive!")
            print("API Details:", json.dumps(data, indent=2))
            sys.exit(0)
        else:
            print(f"FAILED: Backend returned HTTP status {response.status}")
            sys.exit(1)
except Exception as e:
    print(f"FAILED: Could not connect to backend server at {URL}. Error: {str(e)}")
    print("Please make sure uvicorn is running on port 8000.")
    sys.exit(1)
