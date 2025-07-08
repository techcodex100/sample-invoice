from fastapi import FastAPI, Response
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import threading

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"

# ✅ Font Setup (Bold Arial or fallback)
try:
    FONT = ImageFont.truetype("arialbd.ttf", 30)
except:
    FONT = ImageFont.load_default()

TEMPLATE_PATH = "Your paragraph text.png"

# ✅ Pydantic Model
class InvoiceData(BaseModel):
    exporter: str
    invoice_no: str
    exporter_ref: str
    consignee: str
    buyer: str
    place_of_receipt: str
    origin: str
    destination: str
    vessel: str
    port_loading: str
    port_discharge: str
    final_destination: str
    pre_carriage_by: str
    terms_delivery: str
    payment_terms: str
    hs_codes: list[str]
    marks_and_nos: list[str]
    packages: list[str]
    descriptions: list[str]
    quantities: list[int]
    rates: list[float]
    weights: dict
    total_amount_text: str
    company_name: str

# ✅ Counter logic
def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
            return count

# ✅ Draw text helper
def draw_text(draw, x, y, text):
    draw.text((x, y), str(text), font=FONT, fill="black")

# ✅ Draw grid (optional for debugging)
def draw_grid(draw, width, height, step=50):
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill="lightgray", width=1)
        draw_text(draw, x + 2, 2, x)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill="lightgray", width=1)
        draw_text(draw, 2, y + 2, y)

@app.post("/generate-invoice/")
async def generate_invoice(data: InvoiceData):
    try:
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Uncomment this line if you want to show grid for testing:
        # draw_grid(draw, img.width, img.height)

        # === Fixed Data Fields (without title prefixes) ===
        draw_text(draw, 100, 375, data.exporter)
        draw_text(draw, 1350, 375, data.invoice_no)
        draw_text(draw, 1950, 375, data.exporter_ref)
        draw_text(draw, 100, 615, data.consignee)
        draw_text(draw, 1300, 625, data.buyer)
        draw_text(draw, 100, 850, data.pre_carriage_by)
        draw_text(draw, 700, 850, data.place_of_receipt)
        draw_text(draw, 1350, 875, data.origin)
        draw_text(draw, 1950, 875, data.destination)
        draw_text(draw, 90, 975, data.vessel)
        draw_text(draw, 700, 975, data.port_loading)
        draw_text(draw, 90, 1225, data.port_discharge)
        draw_text(draw, 700, 1225, data.final_destination)
        draw_text(draw, 1350, 1200, data.terms_delivery)
        draw_text(draw, 1350, 1250, data.payment_terms)

        # === Table Columns ===
        table_x = [100, 300, 500, 850, 1275, 1700, 1950, 2200]
        y_start = 1440
        row_height = 55

        for i in range(len(data.hs_codes)):
            y = y_start + i * row_height
            draw_text(draw, table_x[0], y, str(i + 1))
            draw_text(draw, table_x[1], y, data.hs_codes[i])
            draw_text(draw, table_x[2], y, data.marks_and_nos[i])
            draw_text(draw, table_x[3], y, data.packages[i])
            draw_text(draw, table_x[4], y, data.descriptions[i])
            draw_text(draw, table_x[5], y, str(data.quantities[i]))
            draw_text(draw, table_x[6], y, f"{data.rates[i]:.2f}")
            amount = data.quantities[i] * data.rates[i]
            draw_text(draw, table_x[7], y, f"{amount:.2f}")

        # === Footer (data only, no label)
        draw_text(draw, 500, 2250, f"{data.weights.get('net', 'N/A')} KGS")
        draw_text(draw, 500, 2350, f"{data.weights.get('gross', 'N/A')} KGS")
        draw_text(draw, 700, 2450, data.total_amount_text)
        draw_text(draw, 1750, 2600, data.company_name)

        # === Save to PDF ===
        buffer = BytesIO()
        img.save(buffer, format="PDF")
        buffer.seek(0)
        filename = f"invoice_{get_next_counter()}.pdf"

        return Response(content=buffer.read(), media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })

    except Exception as e:
        return Response(content=f"Error: {str(e)}", media_type="text/plain", status_code=500)
