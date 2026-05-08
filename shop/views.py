import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import generics
from .models import HealthProfile
from .serializers import HealthProfileSerializer


class HealthProfileList(generics.ListCreateAPIView):
    queryset = HealthProfile.objects.all()
    serializer_class = HealthProfileSerializer


class BulkUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        # Read Excel and iterate through sheets
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet_name)

            # Logic to handle your specific Excel structure
            # This is a simplified version; we match the columns to your model
            for _, row in df.iterrows():
                HealthProfile.objects.create(
                    name=row.get('Profile Name', 'Unnamed Profile'),
                    category=row.get('Category', 'General'),
                    tests_included=row.get('Tests', ''),
                    purpose=row.get('Purpose', ''),
                    price=row.get('Price', 0.00),
                    is_pet_friendly='Pet' in sheet_name  # Auto-detect pet tests
                )

        return Response({"message": "Data imported successfully!"})
