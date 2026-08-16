from django.db import models


class MedicalTest(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='tests/images/', blank=True, null=True)
    key_benefits = models.TextField(
        help_text="Enter key benefits separated by commas")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class TestParameter(models.Model):
    # This links the parameter directly to the Medical Test
    medical_test = models.ForeignKey(
        MedicalTest, related_name='parameters', on_delete=models.CASCADE)
    # Category is optional, as you requested
    category = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g., 'Lipid Profile' or leave blank")
    name = models.CharField(
        max_length=255, help_text="e.g., 'Total Cholesterol'")
    purpose = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class DiagnosticProfile(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Gym Profile")
    image = models.ImageField(
        upload_to='profiles/images/', blank=True, null=True)
    tests = models.ManyToManyField(MedicalTest, related_name='profiles')
    purpose_section = models.TextField()
    benefits_section = models.TextField()
    best_for_section = models.TextField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    test = models.ForeignKey(
        MedicalTest, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(
        DiagnosticProfile, on_delete=models.SET_NULL, null=True, blank=True)

    patient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True)

    # Payment Tracking
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(
        max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(
        max_length=255, blank=True, null=True)

    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {'Paid' if self.is_paid else 'Pending'}"
