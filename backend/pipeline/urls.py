# pipeline/urls.py
from django.urls import path
from . import views  # Yeh aapke pipeline app ke views.py ko connect karega

urlpatterns = [
    # 🌟 Frontend ke fetch requests ab inhi paths par aayenge:
    path('review-queue/', views.review_queue_view if hasattr(views, 'review_queue_view') else views.ReviewQueueView.as_view(), name='review-queue'),
    path('approved-ledger/', views.approved_ledger_view if hasattr(views, 'approved_ledger_view') else views.ApprovedLedgerView.as_view(), name='approved-ledger'),
    path('upload/', views.upload_view if hasattr(views, 'upload_view') else views.UploadView.as_view(), name='upload'),
    
    # Approve button ke liye row action path
    path('review-queue/<int:row_id>/action/', views.execute_action_view if hasattr(views, 'execute_action_view') else views.ExecuteActionView.as_view(), name='row-action'),
]