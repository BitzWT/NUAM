from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        role = request.data.get("role", "analista")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            return Response({
                "message": "User created successfully",
                "user": {
                    "username": user.username,
                    "role": user.role
                }
            }, status=201)
        except IntegrityError:
            return Response({"error": "Username already exists"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
