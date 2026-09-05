import os

files = [
    r'backend/app/services/reconciliation_service.py',
    r'backend/app/services/exception_service.py',
    r'backend/app/services/dashboard_service.py',
    r'backend/app/schemas/exceptions.py',
    r'backend/app/schemas/dashboard.py',
    r'backend/app/ai/context_builder.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('"USD"', '"INR"').replace("'USD'", "'INR'")
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

faker_path = r'backend/app/data_generation/faker_utils.py'
with open(faker_path, 'r', encoding='utf-8') as file:
    content = file.read()
content = content.replace('min_amount: float = 10.0, max_amount: float = 5000.0', 'min_amount: float = 1000.0, max_amount: float = 500000.0')
with open(faker_path, 'w', encoding='utf-8') as file:
    file.write(content)
