import cv2
import numpy as np
import os

def analyze_crop_health(image_path: str) -> list[dict]:
    """
    1. Preprocessing (Scaling, BGR->RGB, Noise Reduction)
    2. Vegetation Index (VARI computation)
    3. Zoning (KMeans segmentation)
    4. Health Classification 
    5. Metrics Calculation
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # 1. Image Preprocessing
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not decode the image")

    # Handle scaling (resize if too large to speed up KMeans)
    max_dim = 600
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # Convert BGR -> RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Handle noise (Gaussian Blur)
    image_blur = cv2.GaussianBlur(image_rgb, (5, 5), 0)

    # 2. Vegetation Index (VARI)
    # VARI = (Green - Red) / (Green + Red - Blue)
    img_float = image_blur.astype(np.float32)
    R, G, B = cv2.split(img_float)
    
    denominator = (G + R - B)
    denominator[denominator == 0] = 1e-6 # avoid div by zero
    vari = (G - R) / denominator
    vari_clipped = np.clip(vari, -1.0, 1.0) # limit extremes

    # 3. Zoning (KMeans / segmentation)
    # Cluster pixels based on their RGB color features to find morphological zones
    Z = image_blur.reshape((-1, 3))
    Z = np.float32(Z)

    K = 4 # Segment into 4 distinct thematic zones
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    labels_2d = label.reshape((image_blur.shape[0], image_blur.shape[1]))
    total_pixels = image_blur.shape[0] * image_blur.shape[1]
    
    results = []
    
    for k in range(K):
        mask = (labels_2d == k)
        zone_vari = vari_clipped[mask]
        
        if len(zone_vari) == 0:
            continue
            
        pixel_count = np.sum(mask)
        area_pct = (pixel_count / total_pixels) * 100
        
        if area_pct < 2.0: # Skip noise clusters
            continue

        avg_vari = np.mean(zone_vari)
        
        # 4. Health Classification
        # VARI > 0.1 is usually healthy vegetation. VARI < 0 is soil/water.
        score_calc = (avg_vari + 0.15) * 200 
        score = min(max(score_calc, 0), 100)
        
        if score >= 60:
            status = "Healthy"
            action = "No action needed. Maintain regular schedule."
        elif score >= 35:
            status = "Moderate"
            action = "Check for water/nutrient deficiency. Consider irrigation."
        else:
            status = "Stress"
            action = "Urgent: Apply targeted fertilizer and inspect for pest stress."

        # 5. Metrics Calculation & Zone Stats
        results.append({
            "zone_id": f"Cluster-{k+1}",
            "score": float(round(score, 2)),
            "status": status,
            "recommended_action": action,
            "area_percentage": float(round(area_pct, 2)),
            "avg_vari": float(round(avg_vari, 4))
        })

    # Sort results by area percentage descending
    results.sort(key=lambda x: x['area_percentage'], reverse=True)
    
    # 7. Output Mapping (Color overlay green/yellow/red map)
    color_map = {
        "Healthy": (0, 255, 0),        # Green
        "Moderate": (0, 255, 255),     # Yellow
        "Stress": (255, 0, 0)          # Red (RGB format)
    }
    
    overlay = np.zeros_like(image_rgb)
    for res in results:
        k = int(res['zone_id'].split('-')[1]) - 1
        mask = (labels_2d == k)
        overlay[mask] = color_map.get(res['status'], (0,0,0))
        
    # Blend overlay with original image
    blended = cv2.addWeighted(image_rgb, 0.6, overlay, 0.4, 0)
    
    # Encode to base64
    import base64
    blended_bgr = cv2.cvtColor(blended, cv2.COLOR_RGB2BGR) # cv2 expects BGR for encode
    _, buffer = cv2.imencode('.jpg', blended_bgr)
    b64_img = base64.b64encode(buffer).decode('utf-8')
    
    return {"zones": results, "heatmap_base64": b64_img}
