from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from datetime import timedelta
from django.conf import settings

from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    DormitoryAdminCreateSerializer, UserProfileSerializer,
)
from .permissions import CanCreateDormitoryAdmin, IsSelfOrSuperAdmin, IsSuperAdmin, IsDormitoryAdmin
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create_dormitory_admin':
            return [CanCreateDormitoryAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsSelfOrSuperAdmin()]
        elif self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        action = self.action
        if action == 'register':
            return UserRegistrationSerializer
        elif action == 'create_dormitory_admin':
            return DormitoryAdminCreateSerializer
        elif action == 'login':
            return UserLoginSerializer
        elif action == 'reset_password_request':
            return PasswordResetRequestSerializer
        elif action == 'change_password':
            return PasswordChangeSerializer
        elif action == 'reset_password_confirm':
            return PasswordResetConfirmSerializer
        return UserSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'])
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'])
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'], permission_classes=[IsAuthenticated])
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Foydalanuvchi tizimga kirgan emas.")

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Eski parolni tekshirish
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Noto‘g‘ri eski parol'}, status=status.HTTP_400_BAD_REQUEST)

            # Yangi parolni o‘rnatish
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'status': 'Parol muvaffaqiyatli o‘zgartirildi'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'])
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password_request(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = get_random_string(length=32)
                user.reset_password_token = token
                user.reset_password_token_expires = timezone.now() + timedelta(hours=24)
                user.save()

                reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return Response({'status': 'Reset email sent'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'])
    @action(detail=False, methods=['post'], url_path='reset-password-confirm/(?P<token>[^/.]+)',
            permission_classes=[AllowAny])
    def reset_password_confirm(self, request, token=None):
        try:
            # Token orqali foydalanuvchini topish
            user = User.objects.get(
                reset_password_token=token,
                reset_password_token_expires__gt=timezone.now()  # Token muddati o‘tmaganini tekshirish
            )

            # Serializer yordamida yangi parolni tekshirish
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']

                # Yangi parolni o‘rnatish
                user.set_password(new_password)

                # Token va token muddati bo‘shatish
                user.reset_password_token = None
                user.reset_password_token_expires = None
                user.save()

                return Response({'status': 'Password reset successful'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Foydalanuvchi amallari'])
    @action(detail=False, methods=['post'], permission_classes=[IsSuperAdmin])
    def create_dormitory_admin(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role=User.ADMIN)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Dormitory admin created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Override permission classes based on actions.
        """
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsSelfOrSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Customize queryset to allow fetching the current user's profile only
        unless the user is a superadmin or dormitory admin.
        """
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()
        if self.request.user.is_super_admin:
            return UserProfile.objects.all()  # Superadmins can access all profiles
        return UserProfile.objects.filter(user=self.request.user)  # Others can only access their profile

    @swagger_auto_schema(tags=['Profile'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def update(self, request, *args, **kwargs):
        """
        Override update method to prevent changing the user's role or status directly.
        """
        # Remove role and status fields from the update request to prevent manual modification
        request.data.pop('role', None)
        request.data.pop('status', None)
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def partial_update(self, request, *args, **kwargs):
        """
        Override partial update method to prevent changing the user's role or status directly.
        """
        # Remove role and status fields from the partial update request to prevent manual modification
        request.data.pop('role', None)
        request.data.pop('status', None)
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Profile'])
    def perform_create(self, serializer):
        """
        Override to ensure the current user is associated with the profile.
        """
        serializer.save(user=self.request.user)
