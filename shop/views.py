import json
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import DiagnosticProfile, MedicalTest, TestParameter
from .serializers import DiagnosticProfileSerializer, MedicalTestSerializer, TestParameterSerializer

# ViewSets automatically provide `list`, `create`, `retrieve`, `update` and `destroy` actions.


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = MedicalTest.objects.all()
    serializer_class = MedicalTestSerializer

    def perform_create(self, serializer):
        test = serializer.save()
        self._save_parameters(test)
        self._save_profiles(test)

    def perform_update(self, serializer):
        test = serializer.save()
        test.parameters.all().delete()
        self._save_parameters(test)
        self._save_profiles(test)

    def _save_parameters(self, test):
        parameters_json = self.request.data.get('parameters_json')
        if parameters_json:
            params = json.loads(parameters_json)
            for p in params:
                if p.get('name'):
                    TestParameter.objects.create(
                        medical_test=test,
                        category=p.get('category', ''),
                        name=p.get('name', ''),
                        purpose=p.get('purpose', '')
                    )

    def _save_profiles(self, test):
        profiles_json = self.request.data.get('profiles_json')
        if profiles_json is not None:
            profile_ids = json.loads(profiles_json)
            # This safely links the test to the chosen profiles
            test.profiles.set(profile_ids)


class TestParameterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = TestParameter.objects.all()
    serializer_class = TestParameterSerializer
