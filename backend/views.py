import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import the service function we wrote in Step 1
from services import analyze_crop_health

@csrf_exempt
def analyze_crop_view(request):
    """
    Accepts a POST request with 'crop_images'.
    Temporarily saves uploaded files, calls the analysis service,
    and returns an aggregated JSON response.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)

    images = request.FILES.getlist('crop_images')
    if not images:
        if 'crop_image' in request.FILES:
            images = [request.FILES['crop_image']]
        else:
            return JsonResponse({'error': 'No images uploaded. Please provide "crop_images".'}, status=400)

    # Validate file format
    allowed_content_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff']
    for img in images:
        if img.content_type not in allowed_content_types:
            return JsonResponse({'error': f'Unsupported format "{img.content_type}". Upload JPEG/PNG/TIFF.'}, status=400)

    try:
        all_zones_data = []
        all_heatmaps = []
        for img in images:
            temp_path = None
            ext = os.path.splitext(img.name)[1]
            if not ext:
                ext = '.jpg'

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                for chunk in img.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # Process AI analysis per file
            analysis_result = analyze_crop_health(temp_path)
            all_zones_data.append(analysis_result["zones"])
            if "heatmap_base64" in analysis_result:
                all_heatmaps.append(analysis_result["heatmap_base64"])
            
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        if not all_zones_data:
            return JsonResponse({'error': 'Image processing returned no zones data.'}, status=500)

        # Aggregate across all images correctly with flattening and area_percentages
        num_images = max(len(images), 1)
        flat_zones = []
        for img_zones in all_zones_data:
            if isinstance(img_zones, list):
                for z in img_zones:
                    if isinstance(z, dict):
                        flat_zones.append(z)
            elif isinstance(img_zones, dict):
                flat_zones.append(img_zones)
            
        # Re-index zone IDs safely
        for i, z in enumerate(flat_zones):
            if isinstance(z, dict):
                z['zone_id'] = f"Zone-{i+1}"
            
        # Sort by area (safely handle missing keys)
        flat_zones.sort(key=lambda x: x.get('area_percentage', 0) if isinstance(x, dict) else 0, reverse=True)
        # Cap to top 6 so frontend UI doesn't blow up with too many divs
        top_zones = flat_zones[:6]

        # Calculate weighted average score (using area_percentage relative to num_images)
        total_weighted_score = sum(z['score'] * (z.get('area_percentage', 100) / 100) for z in flat_zones)
        overall_health_average = float(round(total_weighted_score / num_images, 2))
        
        # Calculate distinct Health / Moderate / Stress % directly from the zone classifications!
        healthy_pct = float(sum(z.get('area_percentage',0) for z in flat_zones if z['status'] == 'Healthy') / num_images)
        moderate_pct = float(sum(z.get('area_percentage',0) for z in flat_zones if z['status'] == 'Moderate') / num_images)
        stress_pct = float(sum(z.get('area_percentage',0) for z in flat_zones if z['status'] == 'Stress') / num_images)

        # Fill potential gaps
        total_computed = healthy_pct + moderate_pct + stress_pct
        if total_computed < 100:
            diff = 100 - total_computed
            if healthy_pct > 0: healthy_pct += diff
            elif moderate_pct > 0: moderate_pct += diff
            elif stress_pct > 0: stress_pct += diff

        # Time to Yield Simulation
        if overall_health_average >= 80:
            yield_time = "14 - 21 Days"
            yield_status = "On Track"
        elif overall_health_average >= 60:
            yield_time = "21 - 28 Days"
            yield_status = "Slight Delay"
        elif overall_health_average >= 40:
            yield_time = "28 - 35 Days"
            yield_status = "Delayed"
        else:
            yield_time = "35+ Days"
            yield_status = "Critical Risk"

        return JsonResponse({
            'status': 'success',
            'overall_health_average': overall_health_average,
            'zones_data': top_zones,
            'heatmap_image': all_heatmaps[0] if all_heatmaps else None,
            'yield_simulation': {
                'estimated_days': yield_time,
                'status': yield_status
            },
            'breakdown': {
                'healthy': float(round(healthy_pct, 1)),
                'water_stress': float(round(moderate_pct, 1)), # Mapping "Moderate" to "Water Stress" in UI
                'nutrient_stress': float(round(stress_pct * 0.5, 1)), # Splitting structural stress 
                'pest_stress': float(round(stress_pct * 0.5, 1))
            }
        }, status=200)

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        # Log to terminal
        print("Backend Error:", err_msg)
        return JsonResponse({'error': f'An internal error occurred: {err_msg}'}, status=500)
