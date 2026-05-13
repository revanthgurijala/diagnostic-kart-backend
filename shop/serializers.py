from rest_framework import serializers
from .models import MedicalTest, DiagnosticProfile, TestParameter


class TestParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestParameter
        fields = '__all__'


class MedicalTestSerializer(serializers.ModelSerializer):
    # Pull in the nested parameters
    parameters = TestParameterSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalTest
        fields = '__all__'


class DiagnosticProfileSerializer(serializers.ModelSerializer):
    tests = MedicalTestSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosticProfile
        fields = '__all__'
