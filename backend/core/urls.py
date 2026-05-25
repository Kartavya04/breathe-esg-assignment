from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.models import User
# Aapke classes ko direct import kar rahe hain yahan
from pipeline.views import DataIngestionAPIView, AnalystReviewQueueView, ApprovedLedgerView, ProcessRowActionView

def home_view(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'password123')
    
    html_content = """
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1>Backend is Live & Running!</h1>
            <br/>
            <a href="/admin/" style="padding: 10px 20px; background-color: #417690; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Go to Admin Panel
            </a>
        </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    # Main Admin & Home
    path('admin/', admin.site.urls),
    path('', home_view),
    
    # 🌟 DIRECT MAPPING (No pipeline/urls.py required)
    path('api/review-queue/', AnalystReviewQueueView.as_view(), name='review-queue'),
    path('api/approved-ledger/', ApprovedLedgerView.as_view(), name='approved-ledger'),
    path('api/upload/', DataIngestionAPIView.as_view(), name='upload'),
    path('api/review-queue/<int:pk>/action/', ProcessRowActionView.as_view(), name='row-action'),
]