from django.urls import path
from .views import HealthProfileList, BulkUploadView

urlpatterns = [
    path('api/profiles/', HealthProfileList.as_view(), name='profile-list'),
    path('api/bulk-upload/', BulkUploadView.as_view(),
         name='bulk-upload'),  # New link
]
