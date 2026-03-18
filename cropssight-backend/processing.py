import cv2
import numpy as np
import base64

def process_image(img_file):
    # Read image from file-like object
    npimg = np.frombuffer(img_file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file")

    # Resize to speed up processing and standardize grid
    max_dim = 800
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    h, w = img.shape[:2]

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define color ranges
    # Green (Healthy)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Yellow (Moderate)
    lower_yellow = np.array([20, 40, 40])
    upper_yellow = np.array([34, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Brown / dark red (Critical)
    lower_brown = np.array([0, 40, 40])
    upper_brown = np.array([19, 255, 255])
    mask_brown1 = cv2.inRange(hsv, lower_brown, upper_brown)
    
    lower_brown2 = np.array([160, 40, 40])
    upper_brown2 = np.array([179, 255, 255])
    mask_brown2 = cv2.inRange(hsv, lower_brown2, upper_brown2)
    
    mask_brown = cv2.bitwise_or(mask_brown1, mask_brown2)

    # Create overlay
    overlay = img.copy()
    overlay[mask_green > 0] = [0, 230, 118]   # Vibrant Green in BGR
    overlay[mask_yellow > 0] = [0, 255, 255] # Cyan/Yellow in BGR depending on format, Yellow= [0, 255, 255] in BGR
    overlay[mask_brown > 0] = [0, 0, 255]     # Red in BGR

    # Blend overlay with original
    # We use alpha=0.6 for the heatmap colors to be visible while keeping the original structure underneath
    alpha = 0.6
    heatmap = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # Calculate Grid (3x3)
    grid_h = h // 3
    grid_w = w // 3
    
    zones = []
    total_score = 0
    zone_count = 0

    for i in range(3):
        for j in range(3):
            y_start = i * grid_h
            y_end = (i + 1) * grid_h if i < 2 else h
            x_start = j * grid_w
            x_end = (j + 1) * grid_w if j < 2 else w
            
            zone_green = mask_green[y_start:y_end, x_start:x_end]
            zone_yellow = mask_yellow[y_start:y_end, x_start:x_end]
            zone_brown = mask_brown[y_start:y_end, x_start:x_end]

            g_count = cv2.countNonZero(zone_green)
            y_count = cv2.countNonZero(zone_yellow)
            b_count = cv2.countNonZero(zone_brown)
            
            total_pixels = g_count + y_count + b_count
            
            if total_pixels == 0:
                health_score = 100 # Default if empty (e.g. bare soil might not be captured properly, assuming 100 or 0)
                label = "No Data"
            else:
                # Score: Green = 100, Yellow = 50, Brown = 0
                health_score = (g_count * 100 + y_count * 50) / total_pixels
                
                if health_score >= 80:
                    label = "Healthy"
                elif health_score >= 50:
                    label = "Moderate Stress"
                else:
                    label = "Critical Stress"
            
            zone_idx = i * 3 + j + 1
            zones.append({
                "id": zone_idx,
                "score": round(health_score),
                "label": label
            })
            
            if total_pixels > 0:
                total_score += health_score
                zone_count += 1
                
            # Draw grid lines
            cv2.rectangle(heatmap, (x_start, y_start), (x_end, y_end), (255, 255, 255), 2)
            # Add zone label
            cv2.putText(heatmap, f"Z{zone_idx}", (x_start + 10, y_start + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    avg_score = round(total_score / zone_count) if zone_count > 0 else 0

    # Add Legend to the heatmap
    legend_w = 160
    legend_h = 110
    legend_x = w - legend_w - 15  # Top right
    legend_y = 15
    
    # Semi-transparent background for legend
    legend_overlay = heatmap.copy()
    cv2.rectangle(legend_overlay, (legend_x, legend_y), (legend_x + legend_w, legend_y + legend_h), (0, 0, 0), -1)
    heatmap = cv2.addWeighted(legend_overlay, 0.65, heatmap, 0.35, 0)
    cv2.rectangle(heatmap, (legend_x, legend_y), (legend_x + legend_w, legend_y + legend_h), (255, 255, 255), 1)
    
    # Draw legend items
    # Healthy (Green)
    cv2.rectangle(heatmap, (legend_x + 10, legend_y + 15), (legend_x + 30, legend_y + 35), (0, 230, 118), -1)
    cv2.putText(heatmap, "Healthy", (legend_x + 40, legend_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    # Moderate (Yellow)
    cv2.rectangle(heatmap, (legend_x + 10, legend_y + 45), (legend_x + 30, legend_y + 65), (0, 255, 255), -1)
    cv2.putText(heatmap, "Moderate", (legend_x + 40, legend_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    # Critical (Red)
    cv2.rectangle(heatmap, (legend_x + 10, legend_y + 75), (legend_x + 30, legend_y + 95), (0, 0, 255), -1)
    cv2.putText(heatmap, "Critical", (legend_x + 40, legend_y + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Encode to base64
    _, buffer = cv2.imencode('.jpg', heatmap)
    b64_img = base64.b64encode(buffer).decode('utf-8')
    
    # Generate insights
    insights = []
    if avg_score < 70:
        insights.append("Widespread stress detected. Consider full-field inspection.")
    critical_zones = [z['id'] for z in zones if z['label'] == 'Critical Stress']
    if critical_zones:
        insights.append(f"Critical stress in zones {', '.join(map(str, critical_zones))}. Check for disease or severe drought.")
    moderate_zones = [z['id'] for z in zones if z['label'] == 'Moderate Stress']
    if moderate_zones:
        insights.append(f"Moderate stress in zones {', '.join(map(str, moderate_zones))}. Adjust irrigation and check nutrient levels.")
    if avg_score >= 85:
        insights.append("Crop health is generally excellent. Maintain current care algorithms.")
        
    if not insights:
        insights.append("Health is stable. Routine monitoring recommended.")

    return {
        "image": f"data:image/jpeg;base64,{b64_img}",
        "score": avg_score,
        "zones": zones,
        "insights": insights
    }


def process_vari_image(img_file):
    # Read image from file-like object
    npimg = np.frombuffer(img_file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file")

    # Resize to speed up processing
    max_dim = 800
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    # Convert to float for calculation
    b, g, r = cv2.split(img.astype(float))
    
    # Calculate VARI: (Green - Red) / (Green + Red - Blue + epsilon)
    epsilon = 1e-6
    vari = (g - r) / (g + r - b + epsilon)
    
    # Normalize VARI to 0-255 for visualization
    vari_normalized = cv2.normalize(vari, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Apply colormap (Jet works well for vegetation indices: red=low, green/blue=high)
    vari_colormap = cv2.applyColorMap(vari_normalized, cv2.COLORMAP_JET)
    
    # Calculate an average health score based on positive VARI percentage
    # Typically VARI > 0 indicates healthy vegetation
    healthy_pixels = np.sum(vari > 0)
    total_pixels = vari.size
    health_score = round((healthy_pixels / total_pixels) * 100) if total_pixels > 0 else 0
    
    insights = []
    if health_score > 70:
        insights.append("VARI indicates strong vegetative health across most of the field.")
    elif health_score > 40:
        insights.append("VARI shows moderate vegetative cover. Review areas with negative VARI for bare soil or stress.")
    else:
        insights.append("Low vegetative health detected. Large portions may be bare soil, dead crops, or severely stressed.")
        
    _, buffer = cv2.imencode('.jpg', vari_colormap)
    b64_img = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "image": f"data:image/jpeg;base64,{b64_img}",
        "score": health_score,
        "insights": insights
    }


def process_kmeans_image(img_file, k=3):
    import cv2
    import numpy as np
    import base64
    from sklearn.cluster import KMeans

    # Read image
    npimg = np.frombuffer(img_file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file")

    # Resize to speed up processing
    max_dim = 800
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    h, w = img.shape[:2]
    
    # Convert to RGB and reshape
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = rgb_img.reshape((-1, 3))
    
    # Downsample pixels if too large to speed up kmeans
    if len(pixels) > 100000:
        sample_indices = np.random.choice(len(pixels), 100000, replace=False)
        sample_pixels = pixels[sample_indices]
    else:
        sample_pixels = pixels
    
    # Calculate kmeans on sample
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(sample_pixels)
    
    # Predict on all pixels
    labels = kmeans.predict(pixels)
    
    # Centers in RGB
    centers = kmeans.cluster_centers_
    
    # Determine which is green, yellow, brown roughly by (G - R)
    greenness = centers[:, 1] - centers[:, 0]
    sorted_indices = np.argsort(greenness)[::-1] # highest greenness first
    
    theme_colors = [
        [22, 163, 74],   # Healthy (Green)
        [217, 119, 6],   # Moderate (Yellow)
        [150, 50, 50]    # Critical (Brown/Red)
    ]
    
    # Create segmented image in RGB
    segmented_img = np.zeros_like(pixels)
    for i in range(k):
        # find rank of cluster i
        rank = np.where(sorted_indices == i)[0][0]
        # map to theme color
        segmented_img[labels == i] = theme_colors[rank] if rank < len(theme_colors) else [0,0,0]
        
    segmented_img = segmented_img.reshape((h, w, 3))
    segmented_bgr = cv2.cvtColor(np.uint8(segmented_img), cv2.COLOR_RGB2BGR)
    
    # Calculate percentages
    counts = np.bincount(labels)
    total_pixels_count = len(labels)
    
    # Sort counts by the ranked indices
    sorted_percentages = []
    for i in range(k):
        orig_cluster_idx = sorted_indices[i]
        percent = (counts[orig_cluster_idx] / total_pixels_count) * 100
        sorted_percentages.append(round(percent, 1))
    
    # Pad to 3 just in case k<3
    while len(sorted_percentages) < 3:
        sorted_percentages.append(0.0)
        
    insights = [
        "KMeans segmentation completed.",
        f"Healthy Zone: {sorted_percentages[0]}%, Moderate Stress: {sorted_percentages[1]}%, Critical Stress: {sorted_percentages[2]}%."
    ]
    
    _, buffer = cv2.imencode('.jpg', segmented_bgr)
    b64_img = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "image": f"data:image/jpeg;base64,{b64_img}",
        "healthy_percent": sorted_percentages[0],
        "moderate_percent": sorted_percentages[1],
        "critical_percent": sorted_percentages[2],
        "insights": insights
    }
