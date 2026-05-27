from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.generic import TemplateView
# Aapke classes ko direct import kar rahe hain yahan
from pipeline.views import DataIngestionAPIView, AnalystReviewQueueView, ApprovedLedgerView, ProcessRowActionView

# Superuser auto-create logic humne yahan barkarar rakhi hai taaki password galat na bataye
def create_admin_if_not_exists():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'password123')

# Isko call kar dete hain taaki server start hote hi admin ready rahe
try:
    create_admin_if_not_exists()
except Exception:
    pass

urlpatterns = [
    # 1. Main Admin Panel
    path('admin/', admin.site.urls),
    
    # 2. 🌟 DIRECT API MAPPING
    path('api/review-queue/', AnalystReviewQueueView.as_view(), name='review-queue'),
    path('api/approved-ledger/', ApprovedLedgerView.as_view(), name='approved-ledger'),
    path('api/upload/', DataIngestionAPIView.as_view(), name='upload'),
    path('api/review-queue/<int:pk>/action/', ProcessRowActionView.as_view(), name='row-action'),

    # 3. 🎯 SINGLE LINK FRONTEND ROUTER
    # Jab koi main domain ya koi aur page khole, toh seedha Frontend ka index.html render hoga
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='frontend'),
]