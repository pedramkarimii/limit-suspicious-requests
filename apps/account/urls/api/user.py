from django.urls import path
from apps.account.views.views_api import user

urlpatterns = [
    path('user-update/<int:pk>/', user.UserUpdateAPI.as_view(), name='user-update'),
    path('user-detail/<int:pk>/', user.DetailAPI.as_view(), name='user-detail'),
    path('user-list/', user.UserListAPI.as_view(), name='user-list'),
    path("user-change-password/<int:pk>/", user.ChangePasswordAPI.as_view(), name="user-change-password"),
    path('user-delete/<int:pk>/', user.UserDeleteAPI.as_view(), name='user-delete'),
]
"""
Maps the URL 'user-update/<int:pk>/' to the UserUpdateAPI.
Maps the URL 'user-detail/<int:pk>/' to the DetailAPI.
Maps the URL 'user-list/' to the UserListAPI.
Maps the URL 'user-change-password/<int:pk>/' to the ChangePasswordAPI.
Maps the URL 'user-delete/<int:pk>/' to the UserDeleteAPI.
"""
