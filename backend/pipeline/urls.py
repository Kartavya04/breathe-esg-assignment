# pipeline/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Pending Audit Queue mapping
    path('review-queue/', views.AnalystReviewQueueView.as_view(), name='review-queue'),
    
    # 2. Approved Ledger History Log mapping
    path('approved-ledger/', views.ApprovedLedgerView.as_view(), name='approved-ledger'),
    
    # 3. Data Ingestion Upload Pipeline mapping
    path('upload/', views.DataIngestionAPIView.as_view(), name='upload'),
    
    # 4. Action Button Engine (pk ko row_id se map kiya taaki frontend se match kare)
    path('review-queue/<int:pk>/action/', views.ProcessRowActionView.as_view(), name='row-action'),
]