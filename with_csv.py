import requests
import time
import os
import csv
import ast  # ✅ Used to safely evaluate list/dict strings
import psutil

# ✅ Correct endpoint
url = "https://sample-invoice.onrender.com/generate-invoice/"

# ✅ CSV input
INPUT_CSV = "invoice_input_50.csv"

# ✅ Folder to save PDFs
SAVE_FOLDER = "generated_invoices"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# ✅ Performance tracking
start_time = time.time()
process = psutil.Process(os.getpid())

success_count = 0
fail_count = 0

with open(INPUT_CSV, mode='r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for i, row in enumerate(reader):
        print(f"\n🔄 Sending invoice #{i + 1}")

        # ✅ Convert string lists to actual lists/dicts
        try:
            row["hs_codes"] = ast.literal_eval(row["hs_codes"])
            row["marks_and_nos"] = ast.literal_eval(row["marks_and_nos"])
            row["packages"] = ast.literal_eval(row["packages"])
            row["descriptions"] = ast.literal_eval(row["descriptions"])
            row["quantities"] = ast.literal_eval(row["quantities"])
            row["rates"] = ast.literal_eval(row["rates"])
            row["weights"] = ast.literal_eval(row["weights"])
        except Exception as e:
            print(f"⚠️ Error parsing row {i+1}: {e}")
            fail_count += 1
            continue

        try:
            response = requests.post(url, json=row)
            if response.status_code == 200:
                pdf_path = os.path.join(SAVE_FOLDER, f"invoice_{i + 1}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ PDF saved: {pdf_path}")
                success_count += 1
            else:
                print(f"❌ Failed: {response.status_code} -> {response.text}")
                fail_count += 1
        except Exception as e:
            print(f"🔥 Error: {e}")
            fail_count += 1

        time.sleep(1)

# ✅ Performance metrics
end_time = time.time()
total_time = round(end_time - start_time, 2)
memory_used = process.memory_info().rss / (1024 * 1024)
cpu_usage = psutil.cpu_percent(interval=1)

print("\n📊 FINAL REPORT")
print(f"✅ Success: {success_count}")
print(f"❌ Failed: {fail_count}")
print(f"🕒 Total Time: {total_time} seconds")
print(f"🧠 Memory Used: {round(memory_used, 2)} MB")
print(f"⚙️ CPU Usage: {cpu_usage}%")
