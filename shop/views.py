from rest_framework import generics
from .models import DiagnosticProfile, MedicalTest
from .serializers import DiagnosticProfileSerializer, MedicalTestSerializer


class ProfileListView(generics.ListAPIView):
    queryset = DiagnosticProfile.objects.all()
    serializer_class = DiagnosticProfileSerializer


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = DiagnosticProfile.objects.all()
    serializer_class = DiagnosticProfileSerializer


class MedicalTestDetailView(generics.RetrieveAPIView):
    queryset = MedicalTest.objects.all()
    serializer_class = MedicalTestSerializer
