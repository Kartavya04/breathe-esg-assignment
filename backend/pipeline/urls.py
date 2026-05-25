# pipeline/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 🌟 Agar aapke views.py mein functions hain:
    path('review-queue/', views.review_queue_view, name='review-queue'),
    path('approved-ledger/', views.approved_ledger_view, name='approved-ledger'),
    path('upload/', views.upload_view, name='upload'),
    path('review-queue/<int:row_id>/action/', views.execute_action_view, name='row-action'),
]