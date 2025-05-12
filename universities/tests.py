from django.test import TestCase
from django.contrib.auth import get_user_model
from universities.models import University, Faculty


class UniversityTestCase(TestCase):
    def setUp(self):
        # Universitet yaratish
        self.university = University.objects.create(
            name='Andijon Texnika Universiteti',
            city='Andijon',
            address='Andijon sh., Ko\'chasi 10',
            description='Andijon Texnika Universitetining tavsifi.',
            contact_info='Telefon: 123-456-789, Email: info@andijon.uz',
            website='https://www.andijon.uz',
        )

    def test_university_creation(self):
        # Universitetning nomini tekshirish
        self.assertEqual(self.university.name, 'Andijon Texnika Universiteti')
        self.assertEqual(self.university.city, 'Andijon')
        self.assertEqual(self.university.contact_info, 'Telefon: 123-456-789, Email: info@andijon.uz')
        self.assertEqual(self.university.website, 'https://www.andijon.uz')

    def test_university_str(self):
        # Universitetning __str__ metodini tekshirish
        self.assertEqual(str(self.university), 'Andijon Texnika Universiteti')


class FacultyTestCase(TestCase):
    def setUp(self):
        # Universitet yaratish
        self.university = University.objects.create(
            name='Andijon Texnika Universiteti',
            city='Andijon',
            address='Andijon sh., Ko\'chasi 10',
        )

        # Fakultet yaratish
        self.faculty = Faculty.objects.create(
            university=self.university,
            name='Informatika Fakulteti',
        )

    def test_faculty_creation(self):
        # Fakultetning nomini tekshirish
        self.assertEqual(self.faculty.name, 'Informatika Fakulteti')
        self.assertEqual(self.faculty.university.name, 'Andijon Texnika Universiteti')

    def test_faculty_str(self):
        # Fakultetning __str__ metodini tekshirish
        self.assertEqual(str(self.faculty), 'Andijon Texnika Universiteti - Informatika Fakulteti')

    def test_unique_faculty_per_university(self):
        # Fakultetning unikaligi (unique_together)
        with self.assertRaises(Exception):  # Exception should be raised due to unique_together constraint
            Faculty.objects.create(
                university=self.university,
                name='Informatika Fakulteti',  # Duplicate faculty name for the same university
            )
