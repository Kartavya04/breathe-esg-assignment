from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import User
from django.http import HttpResponse  # <--- Ye line add karo!

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        return HttpResponse("Admin created! Now go to /admin/")
    return HttpResponse("Admin already exists!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-admin/', create_admin),
]