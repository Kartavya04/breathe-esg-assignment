from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# A simple view for the home page
def home_view(request):
    return HttpResponse("Backend is live and running!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),  # This handles the root URL '/'
    # path('api/', include('your_app_name.urls')), # Uncomment your actual API routes
]