import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django; django.setup()
from services import analyze_crop_health
import numpy as np, cv2
img = np.zeros((100, 100, 3), dtype=np.uint8); cv2.imwrite('dummy.jpg', img)
analysis_result = analyze_crop_health('dummy.jpg')
print('Type of result:', type(analysis_result))
print('Type of zones:', type(analysis_result.get('zones')))
all_zones = [analysis_result['zones']]
flat_zones = []
for z in all_zones: flat_zones.extend(z)
for i, z in enumerate(flat_zones):
    z['zone_id'] = f'Zone-{i+1}'
print('Done!')