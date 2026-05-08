from rest_framework import serializers
from .models import HealthProfile


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = '__all__'
