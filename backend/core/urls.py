from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("<h1>Backend is live!</h1><p>Go to <a href='/admin/'>/admin/</a> to log in.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),  # Root URL par standard message set kar diya
]