from django.urls import path
from .views import (
    ProductView,
    ListProductView
)
urlpatterns = [
    path('add-prod/',ProductView.as_view()),
    path('update-prod/<int:pk>',ProductView.as_view()),
    path('get-prod/',ListProductView.as_view()),
    path('get-prod/<int:pk>',ProductView.as_view()),
    path('delete-prod/<int:pk>',ProductView.as_view()),
]
