from django.urls import path
from .views import (
    DataIngestionAPIView,     # 🟢 Matches views.py perfectly now!
    AnalystReviewQueueView,
    ApprovedLedgerView,   
    ProcessRowActionView
)

urlpatterns = [
    # 1. Maps directly to: http://127.0.0.1:8000/api/upload/
    path('upload/', DataIngestionAPIView.as_view(), name='pipeline-upload'),
    
    # 2. Maps directly to: http://127.0.0.1:8000/api/review-queue/
    path('review-queue/', AnalystReviewQueueView.as_view(), name='review-queue-list'),
    
    # 3. Maps directly to: http://127.0.0.1:8000/api/approved-ledger/
    path('approved-ledger/', ApprovedLedgerView.as_view(), name='approved-ledger-list'),
    
    # 4. Maps directly to: http://127.0.0.1:8000/api/review-queue/<id>/action/
    path('review-queue/<int:pk>/action/', ProcessRowActionView.as_view(), name='review-queue-action'),
]