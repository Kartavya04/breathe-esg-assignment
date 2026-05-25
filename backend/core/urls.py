from django.contrib import admin
from django.urls import path, include  # 🌟 include ko import kar liya
from django.http import HttpResponse
from django.contrib.auth.models import User

def home_view(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'password123')
    
    html_content = """
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1>🚀 Backend is Live & Running!</h1>
            <br/>
            <a href="/admin/" style="padding: 10px 20px; background-color: #417690; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Go to Admin Panel
            </a>
        </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    
    # 🌟 Aapke app ka naam 'pipeline' hai, isliye humne use yahan connect kar diya:
    path('api/', include('pipeline.urls')),  
]