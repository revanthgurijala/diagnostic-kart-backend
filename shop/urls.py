from django.urls import path
from . import views

urlpatterns = [
    path('api/profiles/', views.ProfileListView.as_view(), name='profile-list'),
    path('api/profiles/<int:pk>/',
         views.ProfileDetailView.as_view(), name='profile-detail'),
    path('api/tests/<int:pk>/',
         views.MedicalTestDetailView.as_view(), name='test-detail'),
]
