import requests

try:
    response = requests.get('http://127.0.0.1:5000/api/calendar_events?month=1&year=2026')
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
