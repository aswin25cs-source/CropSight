from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from processing import process_image

load_dotenv('backend/.env')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        # Pass the file object directly
        result = process_image(file)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/vari', methods=['POST'])
def vari():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        from processing import process_vari_image
        result = process_vari_image(file)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/kmeans', methods=['POST'])
def kmeans_route():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    k = request.form.get('k', type=int, default=3)
        
    try:
        from processing import process_kmeans_image
        result = process_kmeans_image(file, k=k)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    
    data = request.get_json()
    if not data or 'id_token' not in data:
        return jsonify({'error': 'Missing id_token'}), 400
        
    token = data['id_token']
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        return jsonify({
            'status': 'success',
            'user': {
                'id': idinfo['sub'],
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture')
            }
        })
    except ValueError:
        return jsonify({'error': 'Invalid ID token'}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
