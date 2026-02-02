import requests
import json

try:
    # Test for January 2026 where we know we have data
    response = requests.get('http://127.0.0.1:5000/api/calendar_events?month=1&year=2026')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        events = response.json()
        print(f"Events found: {len(events)}")
        print(json.dumps(events, indent=2))
    else:
        print("Failed to fetch events")
except Exception as e:
    print(f"Error: {e}")
