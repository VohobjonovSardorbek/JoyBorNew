from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from accounts.permissions import (
    IsSuperAdmin, IsDormitoryAdmin, IsStudent,
    IsAuthenticatedOrSuperAdminOnly, CanCreateDormitoryAdmin, IsSelfOrSuperAdmin
)
from accounts.models import UserProfile, User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    DormitoryAdminCreateSerializer, UserProfileSerializer
)
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from django.urls import reverse



User = get_user_model()

#
# class UserModelTest(TestCase):
#
#     def test_create_regular_user(self):
#         user = User.objects.create_user(
#             username='student1',
#             email='student1@example.com',
#             password='studentpass123',
#             role=User.Role.IS_STUDENT
#         )
#         self.assertEqual(user.username, 'student1')
#         self.assertEqual(user.email, 'student1@example.com')
#         self.assertTrue(user.check_password('studentpass123'))
#         self.assertEqual(user.role, 'student')
#         self.assertTrue(user.is_student)
#         self.assertFalse(user.is_super_admin)
#         self.assertFalse(user.is_dormitory_admin)
#
#     def test_create_dormitory_admin(self):
#         user = User.objects.create_user(
#             username='admin1',
#             email='admin1@example.com',
#             password='adminpass123',
#             role=User.Role.IS_ADMIN
#         )
#         self.assertEqual(user.role, 'admin')
#         self.assertTrue(user.is_dormitory_admin)
#         self.assertFalse(user.is_super_admin)
#         self.assertFalse(user.is_student)
#
#     def test_create_super_admin(self):
#         user = User.objects.create_superuser(
#             username='superadmin1',
#             email='superadmin@example.com',
#             password='superpass123',
#             role=User.Role.IS_SUPERADMIN
#         )
#         self.assertEqual(user.role, 'superadmin')
#         self.assertTrue(user.is_superuser)
#         self.assertTrue(user.is_staff)
#         self.assertTrue(user.is_super_admin)
#         self.assertFalse(user.is_student)
#         self.assertFalse(user.is_dormitory_admin)
#
#     def test_email_required(self):
#         with self.assertRaises(ValueError):
#             User.objects.create_user(
#                 username='user1',
#                 email='',
#                 password='somepass123'
#             )
#
#
# User = get_user_model()
#
#
# class UserProfileModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123',
#             role=User.Role.IS_STUDENT,
#             status='active'
#         )
#
#     def test_user_profile_creation(self):
#         profile = UserProfile.objects.create(
#             user=self.user,
#             phone_number='+998901234567'
#         )
#         self.assertEqual(profile.user, self.user)
#         self.assertEqual(profile.phone_number, '+998901234567')
#         self.assertEqual(profile.user_status, 'active')
#         self.assertFalse(profile.profile_picture)
#
#     def test_phone_number_invalid_format(self):
#         profile = UserProfile(
#             user=self.user,
#             phone_number='901234567'  # not starting with +998
#         )
#         with self.assertRaises(ValidationError):
#             profile.full_clean()  # bu validatsiyani ishga tushuradi
#
#     def test_profile_picture_upload(self):
#         image = SimpleUploadedFile(
#             name='test_image.jpg',
#             content=b'\x47\x49\x46\x38\x39\x61',
#             content_type='image/jpeg'
#         )
#         profile = UserProfile.objects.create(
#             user=self.user,
#             phone_number='+998901234567',
#             profile_picture=image
#         )
#         self.assertTrue(profile.profile_picture.name.startswith('profile_pics/'))
#
#     def test_user_status_property(self):
#         profile = UserProfile.objects.create(
#             user=self.user,
#             phone_number='+998901234567'
#         )
#         self.assertEqual(profile.user_status, self.user.status)
#
#
#
# class PermissionTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.superadmin = User.objects.create_user(username='superadmin', email='superadmin@test.com', password='pass', role='superadmin')
#         self.admin = User.objects.create_user(username='admin', email='admin@test.com', password='pass', role='admin')
#         self.student = User.objects.create_user(username='student', email='student@test.com', password='pass', role='student')
#
#     def get_request(self, user, method='GET'):
#         request = self.factory.generic(method, '/')
#         request.user = user
#         return request
#
#     # IsSuperAdmin
#     def test_is_super_admin_permission(self):
#         perm = IsSuperAdmin()
#         self.assertTrue(perm.has_permission(self.get_request(self.superadmin), None))
#         self.assertFalse(perm.has_permission(self.get_request(self.admin), None))
#
#     # IsDormitoryAdmin
#     def test_is_dormitory_admin_permission(self):
#         perm = IsDormitoryAdmin()
#         self.assertTrue(perm.has_permission(self.get_request(self.admin), None))
#         self.assertFalse(perm.has_permission(self.get_request(self.student), None))
#
#     # IsStudent
#     def test_is_student_permission(self):
#         perm = IsStudent()
#         self.assertTrue(perm.has_permission(self.get_request(self.student), None))
#         self.assertFalse(perm.has_permission(self.get_request(self.superadmin), None))
#
#     # IsAuthenticatedOrSuperAdminOnly
#     def test_is_authenticated_or_superadmin_only_safe(self):
#         perm = IsAuthenticatedOrSuperAdminOnly()
#         request = self.get_request(self.student, method='GET')  # safe method
#         self.assertTrue(perm.has_permission(request, None))
#
#     def test_is_authenticated_or_superadmin_only_unsafe(self):
#         perm = IsAuthenticatedOrSuperAdminOnly()
#         request = self.get_request(self.superadmin, method='POST')  # unsafe method
#         self.assertTrue(perm.has_permission(request, None))
#
#         request = self.get_request(self.student, method='POST')  # unsafe method
#         self.assertFalse(perm.has_permission(request, None))
#
#     # CanCreateDormitoryAdmin
#     def test_can_create_dormitory_admin(self):
#         perm = CanCreateDormitoryAdmin()
#         self.assertTrue(perm.has_permission(self.get_request(self.superadmin), None))
#         self.assertFalse(perm.has_permission(self.get_request(self.admin), None))
#
#     # IsSelfOrSuperAdmin
#     def test_is_self_or_superadmin(self):
#         perm = IsSelfOrSuperAdmin()
#         request = self.get_request(self.student)
#         # User editing own profile
#         class DummyObject:
#             user = self.student
#         self.assertTrue(perm.has_object_permission(request, None, DummyObject()))
#
#         # Superadmin editing someone else's profile
#         request = self.get_request(self.superadmin)
#         self.assertTrue(perm.has_object_permission(request, None, DummyObject()))
#
#         # Admin trying to edit someone else's profile
#         request = self.get_request(self.admin)
#         self.assertFalse(perm.has_object_permission(request, None, DummyObject()))
#
#
#
# class UserSerializerTest(TestCase):
#
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="student", email="student@example.com", password="testpass123"
#         )
#         self.superadmin = User.objects.create_superuser(
#             username="super", email="super@example.com", password="superpass123", role='superadmin'
#         )
#
#     def test_user_registration_serializer_valid(self):
#         data = {
#             "username": "newuser",
#             "email": "newuser@example.com",
#             "password": "newpass123"
#         }
#         serializer = UserRegistrationSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#
#     def test_user_login_serializer_valid(self):
#         data = {
#             "username": "student",
#             "password": "testpass123"
#         }
#         serializer = UserLoginSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#
#     def test_password_change_serializer_mismatch(self):
#         data = {
#             "old_password": "testpass123",
#             "new_password": "newpass123",
#             "confirm_password": "wrongpass"
#         }
#         request = type("Request", (), {"user": self.user})()
#         serializer = PasswordChangeSerializer(data=data, context={'request': request})
#         self.assertFalse(serializer.is_valid())
#
#     def test_password_change_serializer_valid(self):
#         data = {
#             "old_password": "testpass123",
#             "new_password": "newpass123",
#             "confirm_password": "newpass123"
#         }
#         request = type("Request", (), {"user": self.user})()
#         serializer = PasswordChangeSerializer(data=data, context={'request': request})
#         self.assertTrue(serializer.is_valid())
#
#     def test_password_reset_request_serializer_valid(self):
#         data = {
#             "email": "student@example.com"
#         }
#         serializer = PasswordResetRequestSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#
#     def test_password_reset_request_serializer_invalid(self):
#         data = {
#             "email": "unknown@example.com"
#         }
#         serializer = PasswordResetRequestSerializer(data=data)
#         self.assertFalse(serializer.is_valid())
#
#     def test_password_reset_confirm_serializer_match(self):
#         data = {
#             "new_password": "abc123xyz",
#             "confirm_password": "abc123xyz"
#         }
#         serializer = PasswordResetConfirmSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#
#     def test_dormitory_admin_create_serializer_valid(self):
#         data = {
#             "username": "admin1",
#             "email": "admin1@example.com",
#             "password": "adminpass123",
#             "confirm_password": "adminpass123",
#             "first_name": "Admin",
#             "last_name": "One"
#         }
#         serializer = DormitoryAdminCreateSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#         user = serializer.save()
#         self.assertEqual(user.role, User.Role.IS_ADMIN)
#
#     def test_user_profile_serializer_fields_for_superadmin(self):
#         profile = UserProfile.objects.create(user=self.user, phone_number="+998901234567")
#         request = type("Request", (), {"user": self.superadmin})()
#         serializer = UserProfileSerializer(instance=profile, context={"request": request})
#         data = serializer.data
#         self.assertEqual(data['role'], 'student')
#         self.assertEqual(data['status'], 'active')
#
#     def test_user_profile_serializer_fields_for_student(self):
#         profile = UserProfile.objects.create(user=self.user, phone_number="+998901234567")
#         request = type("Request", (), {"user": self.user})()
#         serializer = UserProfileSerializer(instance=profile, context={"request": request})
#         data = serializer.data
#         self.assertIsNone(data['role'])
#         self.assertIsNone(data['status'])



class UserViewSetTests(APITestCase):
    def setUp(self):
        self.password = 'testpassword123'
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password=self.password,
            role='isSuperAdmin'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password=self.password,
            role='isStudent'
        )

    def authenticate(self, user):
        response = self.client.post(reverse('user-login'), {
            'username': user.username,
            'password': self.password
        })
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

    def test_user_register(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(reverse('user-register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_user_login_successful(self):
        data = {'username': self.student.username, 'password': self.password}
        response = self.client.post(reverse('user-login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_login_invalid_credentials(self):
        data = {'username': 'invalid', 'password': 'wrongpass'}
        response = self.client.post(reverse('user-login'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_successful(self):
        self.authenticate(self.student)
        data = {
            'old_password': self.password,
            'new_password': 'newsecurepassword123'
        }
        response = self.client.post(reverse('user-change-password'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        self.authenticate(self.student)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newsecurepassword123'
        }
        response = self.client.post(reverse('user-change-password'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dormitory_admin_by_superadmin(self):
        self.authenticate(self.superadmin)
        data = {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'adminpassword123'
        }
        response = self.client.post(reverse('user-create-dormitory-admin'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'adminuser')

    def test_create_dormitory_admin_by_student_forbidden(self):
        self.authenticate(self.student)
        data = {
            'username': 'adminuser2',
            'email': 'admin2@example.com',
            'password': 'adminpassword123'
        }
        response = self.client.post(reverse('user-create-dormitory-admin'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_password_request_valid(self):
        response = self.client.post(reverse('user-reset-password-request'), {
            'email': self.student.email
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_request_invalid_email(self):
        response = self.client.post(reverse('user-reset-password-request'), {
            'email': 'notfound@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_confirm_success(self):
        token = 'resettoken123'
        self.student.reset_password_token = token
        self.student.reset_password_token_expires = timezone.now() + timedelta(hours=1)
        self.student.save()

        url = reverse('user-reset-password-confirm', kwargs={'token': token})
        response = self.client.post(url, {
            'new_password': 'NewPass1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_confirm_invalid_token(self):
        url = reverse('user-reset-password-confirm', kwargs={'token': 'invalidtoken'})
        response = self.client.post(url, {
            'new_password': 'NewPass1234'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_detail(self):
        self.authenticate(self.student)
        url = reverse('user-detail', kwargs={'pk': self.student.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.student.username)

    def test_user_list_accessible_only_for_authenticated(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate(self.student)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)