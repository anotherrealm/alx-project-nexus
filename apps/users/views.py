from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": serializer.errors
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    }
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "error": {
                    "code": "AUTHENTICATION_ERROR",
                    "message": "Invalid credentials",
                    "details": serializer.errors
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {
                        "status": "error",
                        "error": {
                            "code": "MISSING_TOKEN",
                            "message": "Refresh token is required"
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                    "status": "success",
                    "message": "Logged out successfully"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired refresh token"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(TokenRefreshView):
    """Custom refresh token view with consistent response format."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response(
                {
                    "status": "success",
                    "message": "Token refreshed successfully",
                    "data": response.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "status": "error",
                "error": {
                    "code": "TOKEN_REFRESH_ERROR",
                    "message": "Failed to refresh token",
                    "details": response.data
                }
            },
            status=response.status_code
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "status": "success",
                "data": UserSerializer(user).data
            },
            status=status.HTTP_200_OK,
        )
