import random
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from .models import OTP
from .serializers import EmailSerializer, OTPVerifySerializer
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def request_otp(request):
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user, created = User.objects.get_or_create(username=email, email=email)
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp_code)
        send_mail('Your OTP Code', f'Your OTP is {otp_code}', 'no-reply@example.com', [email])
        return Response({'message': 'OTP sent to email.'})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_input = serializer.validated_data['otp']
        try:
            user = User.objects.get(email=email)
            otp_record = OTP.objects.filter(user=user, code=otp_input, is_verified=False).latest('created_at')
            otp_record.is_verified = True
            otp_record.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        except Exception as e:
            return Response({'error': 'Invalid OTP or email.'}, status=400)
    return Response(serializer.errors, status=400)
