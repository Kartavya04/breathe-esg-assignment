from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Simple view to confirm the backend is alive
def home_view(request):
    return HttpResponse("<h1>Backend is live!</h1><p>Go to <a href='/admin/'>/admin/</a> to log in.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),  # Root URL '/' par ye view chalega
    # Agar aapne koi API app banayi hai, toh uska include yahan add karein:
    # path('api/', include('your_app_name.urls')), 
]