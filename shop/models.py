from django.db import models


class HealthProfile(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    tests_included = models.TextField(
        blank=True, null=True)  # Makes it optional for now
    purpose = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_pet_friendly = models.BooleanField(default=False)

    def __cl__str__(self):
        return self.name
