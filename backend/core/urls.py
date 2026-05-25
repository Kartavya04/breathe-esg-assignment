from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

# Is view se aapko screen par hi clickable links mil jayengi
def home_view(request):
    html_content = """
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1>🚀 Backend is Live & Running!</h1>
            <p>Neeche diye gaye buttons par click karke direct jao:</p>
            <br/>
            <a href="/admin/" style="padding: 10px 20px; background-color: #417690; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px;">
                Go to Admin Panel
            </a>
        </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),  # Ab main link par hi button mil jayega
]