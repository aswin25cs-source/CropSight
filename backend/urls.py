from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

# Import our custom view
from views import analyze_crop_view

def redirect_to_frontend(request):
    return redirect('http://localhost:3000/index.html')

urlpatterns = [
    path('', redirect_to_frontend, name='home'),
    path('admin/', admin.site.urls),
    # Wire the /analyze/ endpoint to our analyzer function
    path('analyze/', analyze_crop_view, name='analyze'),
]
