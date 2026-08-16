import json
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import DiagnosticProfile, MedicalTest, TestParameter, Booking
from .serializers import DiagnosticProfileSerializer, MedicalTestSerializer, TestParameterSerializer, BookingSerializer


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


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Secure it!
    queryset = Booking.objects.all().order_by('-created_at')  # Newest first
    serializer_class = BookingSerializer


# Initialize Razorpay Client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class CreateOrderAPIView(APIView):
    def post(self, request):
        data = request.data
        test_id = data.get('test_id')

        try:
            test = MedicalTest.objects.get(id=test_id)
            # Razorpay expects amount in paise (multiply by 100)
            amount_in_paise = int(test.price * 100)

            # 1. Create Order in Razorpay
            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": "1"  # Auto capture payment
            })

            # 2. Save Pending Booking in our Database
            booking = Booking.objects.create(
                test=test,
                patient_name=data.get('patient_name'),
                phone_number=data.get('phone_number'),
                email=data.get('email'),
                appointment_date=data.get('appointment_date'),
                appointment_time=data.get('appointment_time'),
                amount=test.price,
                razorpay_order_id=razorpay_order['id']
            )

            # 3. Send Order ID to Frontend
            return Response({
                'order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'booking_id': booking.id,
                'key': settings.RAZORPAY_KEY_ID
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentAPIView(APIView):
    def post(self, request):
        data = request.data
        try:
            # 1. Verify the signature securely using Razorpay's utility
            client.utility.verify_payment_signature({
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature')
            })

            # 2. If verification passes, update our database
            booking = Booking.objects.get(
                razorpay_order_id=data.get('razorpay_order_id'))
            booking.is_paid = True
            booking.razorpay_payment_id = data.get('razorpay_payment_id')
            booking.razorpay_signature = data.get('razorpay_signature')
            booking.save()

            if booking.email:
                subject = f"Booking Confirmed: {booking.test.name}"
                message = f"Hello {booking.patient_name},\n\nYour payment of ₹{booking.amount} was successful! Your test ({booking.test.name}) is booked for {booking.appointment_date}.\n\nThank you for choosing Diagnostic Kart."
                send_mail(subject, message,
                          settings.DEFAULT_FROM_EMAIL, [booking.email])

            return Response({'message': 'Payment successful and verified!'})

        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Invalid Payment Signature!'}, status=status.HTTP_400_BAD_REQUEST)


class ContactAPIView(APIView):
    permission_classes = []  # Open to the public

    def post(self, request):
        data = request.data
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        # Format the email that you will receive
        email_subject = f"New Website Inquiry: {subject}"
        email_body = f"Name: {name}\nPhone: {phone}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            # Send to the default admin email configured in settings.py
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL]
            )
            return Response({'message': 'Thank you! Your message has been sent successfully.'})
        except Exception as e:
            return Response({'error': 'Failed to send message.'}, status=400)
