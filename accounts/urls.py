from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserView,ListUser

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_refresh'),
    path('add-user/',UserView.as_view()),
    path('get-user/',ListUser.as_view()),
    path('get-user/<int:pk>',UserView.as_view()),
    path('update-user/<int:pk>',UserView.as_view()),
    path('delete-user/<int:pk>',UserView.as_view()),
]