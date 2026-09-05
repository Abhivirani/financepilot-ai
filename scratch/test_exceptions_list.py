import requests
import json

resp = requests.get("http://127.0.0.1:8000/api/v1/exceptions")
print("Status code:", resp.status_code)
data = resp.json()
print(json.dumps(data["data"], indent=2))
print("\nExceptions Detail List:")
for item in data["data"]["items"]:
    print(f"  {item['transaction_id']}: {item['rule_type']} | {item['title']} | Severity: {item['severity']}")
