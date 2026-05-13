from django.contrib import admin
from .models import MedicalTest, DiagnosticProfile, TestParameter

# This tells Django to show Parameters INSIDE the Medical Test page


class TestParameterInline(admin.TabularInline):
    model = TestParameter
    extra = 1


class MedicalTestAdmin(admin.ModelAdmin):
    inlines = [TestParameterInline]


admin.site.register(MedicalTest, MedicalTestAdmin)
admin.site.register(DiagnosticProfile)
