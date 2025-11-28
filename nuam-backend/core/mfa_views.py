import qrcode
import io
import base64
from django.contrib.auth import authenticate
from django.core.signing import Signer, BadSignature
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice

class SetupMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Create a new unconfirmed device or get existing one
        device, created = TOTPDevice.objects.get_or_create(user=user, confirmed=False)
        
        # Generate QR Code
        url = device.config_url
        img = qrcode.make(url)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return Response({
            "qr_code": f"data:image/png;base64,{img_str}",
            "secret_key": device.key  # Optional: display key for manual entry
        })

class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get("code")
        
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            return Response({"error": "No pending MFA setup found"}, status=400)

        if device.verify_token(code):
            device.confirmed = True
            device.save()
            # Remove any other unconfirmed devices
            TOTPDevice.objects.filter(user=user, confirmed=False).delete()
            return Response({"message": "MFA enabled successfully"})
        
        return Response({"error": "Invalid code"}, status=400)

class LoginMFAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        # Check if user has MFA enabled
        if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            signer = Signer()
            temp_token = signer.sign(user.id)
            return Response({
                "mfa_required": True,
                "temp_token": temp_token
            })
        
        # No MFA, issue tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "mfa_required": False,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "role": user.role
            }
        })

class LoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get("temp_token")
        code = request.data.get("code")
        
        signer = Signer()
        try:
            user_id = signer.unsign(temp_token)
        except BadSignature:
            return Response({"error": "Invalid or expired session"}, status=400)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if not device:
             return Response({"error": "MFA not enabled for this user"}, status=400)

        if device.verify_token(code):
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "username": user.username,
                    "role": user.role
                }
            })
        
        return Response({"error": "Invalid OTP code"}, status=400)
