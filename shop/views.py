import json
from rest_framework import viewsets
from .models import DiagnosticProfile, MedicalTest, TestParameter
from .serializers import DiagnosticProfileSerializer, MedicalTestSerializer, TestParameterSerializer

# ViewSets automatically provide `list`, `create`, `retrieve`, `update` and `destroy` actions.


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticProfile.objects.all()
    serializer_class = DiagnosticProfileSerializer

    # 1. Intercept creation
    def perform_create(self, serializer):
        profile = serializer.save()
        self._save_tests(profile)

    # 2. Intercept update
    def perform_update(self, serializer):
        profile = serializer.save()
        self._save_tests(profile)

    # 3. Read the JSON and link the database tables
    def _save_tests(self, profile):
        tests_json = self.request.data.get('tests_json')
        # We check "is not None" so if you uncheck all boxes, it safely clears the tests
        if tests_json is not None:
            test_ids = json.loads(tests_json)
            # .set() automatically adds new checkboxes and removes unchecked ones!
            profile.tests.set(test_ids)


class MedicalTestViewSet(viewsets.ModelViewSet):
    queryset = MedicalTest.objects.all()
    serializer_class = MedicalTestSerializer

    # Intercept creation to save the nested parameters
    def perform_create(self, serializer):
        test = serializer.save()
        self._save_parameters(test)

    # Intercept update to overwrite the nested parameters
    def perform_update(self, serializer):
        test = serializer.save()
        test.parameters.all().delete()  # Wipe old parameters
        self._save_parameters(test)    # Save new parameters

    # The unpacking logic
    def _save_parameters(self, test):
        parameters_json = self.request.data.get('parameters_json')
        if parameters_json:
            params = json.loads(parameters_json)
            for p in params:
                # We only create it if they actually typed a name
                if p.get('name'):
                    TestParameter.objects.create(
                        medical_test=test,
                        category=p.get('category', ''),
                        name=p.get('name', ''),
                        purpose=p.get('purpose', '')
                    )


class TestParameterViewSet(viewsets.ModelViewSet):
    queryset = TestParameter.objects.all()
    serializer_class = TestParameterSerializer
