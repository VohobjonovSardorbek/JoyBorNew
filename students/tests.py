from datetime import date

from django.test import TestCase
from django.utils import timezone
from decimal import Decimal

from accounts.models import User
from dormitories.models import Dormitory
from universities.models import University, Faculty
from students.models import Student, Application  # yoki to‘g‘ri import qiling
from django.core.files.uploadedfile import SimpleUploadedFile


class StudentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123',
            role=User.Role.IS_STUDENT,
            first_name='Ali',
            last_name='Valiyev',
            email='sardorbek@gmail.com'
        )

        self.university = University.objects.create(name='TATU')
        self.faculty = Faculty.objects.create(name='Dasturiy injiniring', university=self.university)

        self.student = Student.objects.create(
            user=self.user,
            passport_number='AA1234567',
            father_name='Vali Valiyev',
            university=self.university,
            faculty=self.faculty,
            additional_phone='998901112233',
            emergency_contact_name='Ota',
            emergency_contact_phone='998909998877',
            discount='15%',
            social_status='Yolg‘iz ona farzandi'
        )

    def test_student_str(self):
        self.assertEqual(str(self.student), f"{self.user.get_full_name()}")


class ApplicationModelTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='superpass',
            role=User.Role.IS_ADMIN
        )

        self.user = User.objects.create_user(
            username='student2',
            password='testpass456',
            role=User.Role.IS_STUDENT,
            first_name='Hasan',
            last_name='Qodirov',
            email='sardorbek@gmail.com'
        )
        self.university = University.objects.create(name='Test University')

        self.dormitory = Dormitory.objects.create(
            name='Andijon TTJ',
            university=self.university,
            address='Andijon sh., 1-uy',
            city='Andijon',
            number_of_floors=5,
            description='Modern hostel with excellent facilities.',
            subscription_end_date=date(2025, 12, 31),
            status='active',
            admin=self.admin_user,
            contact_info='Phone: 123-456-789, Email: dorm@andijon.uz',
            latitude=41.2406,
            longitude=69.2556
        )

        self.student_document = SimpleUploadedFile("id_card.pdf", b"file_content", content_type="application/pdf")

        self.application = Application.objects.create(
            student=self.user,
            dormitory=self.dormitory,
            student_document=self.student_document,
            status='pending'
        )

    def test_application_str(self):
        expected_str = f"Application by {self.user.get_full_name()} to {self.dormitory.name}"
        self.assertEqual(str(self.application), expected_str)

    def test_application_default_status(self):
        self.assertEqual(self.application.status, 'pending')

    def test_application_has_document(self):
        self.assertTrue(self.application.student_document.name.startswith('student_ID/'))
