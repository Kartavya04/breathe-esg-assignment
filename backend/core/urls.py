from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.models import User

# Yeh function automatically check karega aur admin banayega jab bhi koi website kholega
def home_view(request):
    # Auto-create admin if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        msg = "Backend is Live! (Admin account auto-created)"
    else:
        msg = "Backend is Live & Running!"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1>{msg}</h1>
            <p></p>
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
    path('', home_view),  # Main link par hi sab automatic ho jayega
]