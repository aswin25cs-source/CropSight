import urllib.request

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
with open(r'C:\Users\ADMIN\Downloads\WhatsApp Image 2026-03-19 at 3.23.31 AM.jpeg', 'rb') as f:
    img_data = f.read()

body = (
    b'--' + boundary.encode() + b'\r\n'
    b'Content-Disposition: form-data; name="crop_images"; filename="WhatsApp Image 2026-03-19 at 3.23.31 AM.jpeg"\r\n'
    b'Content-Type: image/jpeg\r\n\r\n' +
    img_data + b'\r\n'
    b'--' + boundary.encode() + b'--\r\n'
)

req = urllib.request.Request(
    'http://127.0.0.1:8000/analyze/', 
    data=body, 
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)

try:
    resp = urllib.request.urlopen(req)
    print("SUCCESS JSON:")
    print(resp.read().decode()[:200]) # Print first 200 chars
except urllib.error.HTTPError as e:
    print("ROUTE ERROR JSON:")
    print(e.read().decode())
except Exception as e:
    import traceback
    print("FATAL:", str(e))
    traceback.print_exc()
