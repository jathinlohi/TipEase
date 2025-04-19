import base64
import json
from io import BytesIO
import qrcode

def generate_qr_code_base64(data: dict) -> str:
    json_data = json.dumps(data)
    encoded_data = base64.urlsafe_b64encode(json_data.encode()).decode()

    url = f"http://localhost:8000/pay/{encoded_data}"  # Modify if deployed

    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Save image to BytesIO
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Convert image to base64 string
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    return img_base64
