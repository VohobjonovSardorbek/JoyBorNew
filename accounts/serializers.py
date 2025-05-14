from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profiles. Shows role and status based on user's permissions.
    """
    role = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'profile_picture', 'status', 'role']
        read_only_fields = ['user', 'status', 'role']

    def get_role(self, obj):
        request = self.context.get('request')
        if request and (request.user.is_super_admin or request.user.is_superuser):
            return obj.user.role
        return None

    def get_status(self, obj):
        request = self.context.get('request')
        if request and (request.user.is_super_admin or request.user.is_dormitory_admin):
            return obj.user.status
        return None

class UserSerializer(serializers.ModelSerializer):
    """
    Base serializer for User model.
    Role field is only visible to superusers and superadmins.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'role', 'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Only show sensitive fields if user is superuser or super_admin
        if request and (request.user.is_superuser or getattr(request.user, 'is_super_admin', False)):
            return data

        # Remove sensitive fields for regular users
        sensitive_fields = ['is_superuser', 'is_staff', 'is_super_admin', 'is_dormitory_admin']
        for field in sensitive_fields:
            data.pop(field, None)

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email'),
            role='student'  # har doim default
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Ensure the new passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        # Ensure email exists in the system
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address not found.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset.
    """
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Ensure passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data


class DormitoryAdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating dormitory admin accounts.
    Only accessible by superusers and superadmins.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate(self, data):
        # Ensure passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        # Assuming 'role' is a field in the User model that uses an enum or constant for dormitory admins
        user = User.objects.create_user(
            **validated_data,
            role=User.Role.IS_ADMIN  # Set the role correctly for dormitory admin
        )
        return user
