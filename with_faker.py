import requests
from faker import Faker
import random
import time

URL = "https://sample-invoice.onrender.com/generate-invoice/"
fake = Faker()

def generate_fake_invoice():
    count = random.randint(1, 5)
    hs_codes = [f"HS{random.randint(100, 999)}" for _ in range(count)]
    marks = [fake.word() for _ in range(count)]
    packages = [fake.word() for _ in range(count)]
    descriptions = [fake.sentence() for _ in range(count)]
    quantities = [random.randint(1, 20) for _ in range(count)]
    rates = [round(random.uniform(100, 1000), 2) for _ in range(count)]
    net_weight = round(random.uniform(100, 500), 2)
    gross_weight = round(net_weight + random.uniform(50, 200), 2)
    total_amount = round(sum([q * r for q, r in zip(quantities, rates)]), 2)

    return {
        "exporter": fake.company(),
        "invoice_no": f"INV-{random.randint(1000, 9999)}",
        "exporter_ref": f"REF-{random.randint(10000, 99999)}",
        "consignee": fake.name(),
        "buyer": fake.name(),
        "place_of_receipt": fake.city(),
        "origin": fake.country(),
        "destination": fake.country(),
        "vessel": fake.word().capitalize(),
        "port_loading": fake.city(),
        "port_discharge": fake.city(),
        "final_destination": fake.city(),
        "pre_carriage_by": "Truck",
        "terms_delivery": "FOB",
        "payment_terms": "Net 30",
        "hs_codes": hs_codes,
        "marks_and_nos": marks,
        "packages": packages,
        "descriptions": descriptions,
        "quantities": quantities,
        "rates": rates,
        "weights": {"net": net_weight, "gross": gross_weight},
        "total_amount_text": f"USD {total_amount}",
        "company_name": fake.company()
    }

success_count = 0
fail_count = 0

for i in range(1, 51):
    try:
        payload = generate_fake_invoice()
        print(f"🔄 Sending invoice #{i}")
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Success: invoice #{i}")
            success_count += 1
        else:
            print(f"❌ Failed: {response.status_code} -> {response.text}")
            fail_count += 1
        time.sleep(1)
    except Exception as e:
        print(f"🔥 Exception on invoice #{i}: {e}")
        fail_count += 1

print("\n📊 Performance:")
print(f"✅ Success: {success_count}")
print(f"❌ Failed: {fail_count}")
