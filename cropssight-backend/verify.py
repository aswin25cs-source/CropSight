import sys
import json
from app import app
import builtins
import io

def test_endpoints():
    client = app.test_client()
    
    # Test VARI
    print("Testing /api/vari...")
    with open('test_crop.jpg', 'rb') as f:
        data = {'image': (f, 'test_crop.jpg')}
        response = client.post('/api/vari', data=data, content_type='multipart/form-data')
    print("VARI status:", response.status_code)
    try:
        vari_data = json.loads(response.data)
        print("VARI keys:", list(vari_data.keys()))
    except:
        print("VARI output non-json")
        
    # Test KMeans
    print("Testing /api/kmeans...")
    with open('test_crop.jpg', 'rb') as f:
        data = {'image': (f, 'test_crop.jpg'), 'k': '3'}
        response = client.post('/api/kmeans', data=data, content_type='multipart/form-data')
    print("KMeans status:", response.status_code)
    try:
        kmeans_data = json.loads(response.data)
        print("KMeans keys:", list(kmeans_data.keys()))
        if 'error' in kmeans_data:
            print("KMeans error:", kmeans_data['error'])
    except:
        print("KMeans output non-json")
        
    # Test Google Auth
    print("Testing /api/auth/google...")
    response = client.post('/api/auth/google', json={'id_token': 'dummy_token'})
    print("Google Auth status:", response.status_code)
    try:
        auth_data = json.loads(response.data)
        print("Google Auth response:", auth_data)
    except:
        pass

if __name__ == '__main__':
    test_endpoints()
