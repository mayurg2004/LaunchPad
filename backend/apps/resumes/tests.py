import io
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, UserRole
from students.models import Student
from .models import Resume

class ResumeAPITests(APITestCase):
    def setUp(self):
        # Create student 1
        self.student_user = User.objects.create_user(
            email='student1@test.com',
            password='password123',
            role=UserRole.STUDENT,
            first_name='Student',
            last_name='One'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            enrollment_number='STU001',
            branch='CSE',
            year=3,
            semester=5,
            cgpa=8.5
        )

        # Create student 2
        self.student_user2 = User.objects.create_user(
            email='student2@test.com',
            password='password123',
            role=UserRole.STUDENT,
            first_name='Student',
            last_name='Two'
        )
        self.student2 = Student.objects.create(
            user=self.student_user2,
            enrollment_number='STU002',
            branch='CSE',
            year=3,
            semester=5,
            cgpa=8.0
        )

        # Create placement officer
        self.officer_user = User.objects.create_user(
            email='officer@test.com',
            password='password123',
            role=UserRole.PLACEMENT_OFFICER,
            first_name='Placement',
            last_name='Officer'
        )

        self.list_create_url = reverse('resume-list')

    def generate_pdf(self, name='test_resume.pdf', size=1024):
        return SimpleUploadedFile(name, b'a' * size, content_type='application/pdf')
        
    def generate_txt(self, name='test_resume.txt'):
        return SimpleUploadedFile(name, b'Hello world', content_type='text/plain')

    def test_1_student_can_upload_pdf(self):
        self.client.force_authenticate(user=self.student_user)
        pdf = self.generate_pdf()
        data = {
            'title': 'My Resume',
            'file': pdf
        }
        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resume.objects.count(), 1)
        self.assertEqual(Resume.objects.first().title, 'My Resume')

    def test_2_non_pdf_rejected(self):
        self.client.force_authenticate(user=self.student_user)
        txt = self.generate_txt()
        data = {
            'title': 'My Resume',
            'file': txt
        }
        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_3_file_too_large_rejected(self):
        self.client.force_authenticate(user=self.student_user)
        # Generate 6MB file
        large_pdf = self.generate_pdf(size=6 * 1024 * 1024)
        data = {
            'title': 'My Large Resume',
            'file': large_pdf
        }
        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_4_student_can_view_own_resumes(self):
        Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        Resume.objects.create(student=self.student, title='R2', file=self.generate_pdf('test2.pdf'))
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_5_student_cannot_view_another_students_resume(self):
        other_resume = Resume.objects.create(student=self.student2, title='R_other', file=self.generate_pdf())
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        detail_url = reverse('resume-detail', kwargs={'pk': other_resume.id})
        response2 = self.client.get(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_6_student_can_update_own_resume(self):
        resume = Resume.objects.create(student=self.student, title='Old Title', file=self.generate_pdf())
        self.client.force_authenticate(user=self.student_user)
        
        detail_url = reverse('resume-detail', kwargs={'pk': resume.id})
        data = {'title': 'New Title'}
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resume.refresh_from_db()
        self.assertEqual(resume.title, 'New Title')

    def test_7_student_can_delete_own_resume(self):
        resume = Resume.objects.create(student=self.student, title='To Delete', file=self.generate_pdf())
        self.client.force_authenticate(user=self.student_user)
        
        detail_url = reverse('resume-detail', kwargs={'pk': resume.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Resume.objects.count(), 0)

    def test_8_only_one_active_resume(self):
        r1 = Resume.objects.create(student=self.student, title='R1', is_active=True, file=self.generate_pdf())
        r2 = Resume.objects.create(student=self.student, title='R2', is_active=False, file=self.generate_pdf('t2.pdf'))
        
        self.client.force_authenticate(user=self.student_user)
        detail_url = reverse('resume-detail', kwargs={'pk': r2.id})
        self.client.patch(detail_url, {'is_active': True})
        
        r1.refresh_from_db()
        r2.refresh_from_db()
        self.assertFalse(r1.is_active)
        self.assertTrue(r2.is_active)

    def test_9_active_resume_endpoint(self):
        Resume.objects.create(student=self.student, title='R1', is_active=False, file=self.generate_pdf('t1.pdf'))
        active_r = Resume.objects.create(student=self.student, title='R2', is_active=True, file=self.generate_pdf('t2.pdf'))
        
        self.client.force_authenticate(user=self.student_user)
        active_url = reverse('resume-active')
        response = self.client.get(active_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], active_r.id)

    def test_10_unauthorized_access(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        detail_url = reverse('resume-detail', kwargs={'pk': resume.id})
        response2 = self.client.get(detail_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_11_version_number_generation(self):
        # first resume gets version 1
        r1 = Resume.objects.create(student=self.student, title='First', file=self.generate_pdf('t1.pdf'))
        self.assertEqual(r1.version_number, 1)

        # second resume gets version 2
        r2 = Resume.objects.create(student=self.student, title='Second', file=self.generate_pdf('t2.pdf'))
        self.assertEqual(r2.version_number, 2)

    def test_12_versions_independent_for_students(self):
        r1 = Resume.objects.create(student=self.student, title='First S1', file=self.generate_pdf('t1.pdf'))
        self.assertEqual(r1.version_number, 1)

        r2 = Resume.objects.create(student=self.student2, title='First S2', file=self.generate_pdf('t2.pdf'))
        self.assertEqual(r2.version_number, 1)

        r3 = Resume.objects.create(student=self.student, title='Second S1', file=self.generate_pdf('t3.pdf'))
        self.assertEqual(r3.version_number, 2)

    def test_13_versions_endpoint_history(self):
        Resume.objects.create(student=self.student, title='First', file=self.generate_pdf('t1.pdf'))
        Resume.objects.create(student=self.student, title='Second', file=self.generate_pdf('t2.pdf'))
        Resume.objects.create(student=self.student, title='Third', file=self.generate_pdf('t3.pdf'))

        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-versions')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered newest version first
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['version_number'], 3)
        self.assertEqual(response.data[0]['title'], 'Third')
        self.assertEqual(response.data[1]['version_number'], 2)
        self.assertEqual(response.data[2]['version_number'], 1)

    def test_14_versions_endpoint_isolation(self):
        Resume.objects.create(student=self.student, title='First S1', file=self.generate_pdf('t1.pdf'))
        Resume.objects.create(student=self.student2, title='First S2', file=self.generate_pdf('t2.pdf'))

        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-versions')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'First S1')

    def test_15_download_own_resume(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf('mydoc.pdf'))
        
        self.client.force_authenticate(user=self.student_user)
        download_url = reverse('resume-download', kwargs={'pk': resume.id})
        response = self.client.get(download_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('mydoc.pdf', response['Content-Disposition'])

    def test_16_download_another_students_resume(self):
        other_resume = Resume.objects.create(student=self.student2, title='R_other', file=self.generate_pdf('other.pdf'))
        
        self.client.force_authenticate(user=self.student_user)
        download_url = reverse('resume-download', kwargs={'pk': other_resume.id})
        response = self.client.get(download_url)
        
        # In ResumeViewSet, get_queryset for student filters to their own resumes, so they get 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_17_download_missing_resume_returns_404(self):
        self.client.force_authenticate(user=self.student_user)
        download_url = reverse('resume-download', kwargs={'pk': 9999})
        response = self.client.get(download_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_18_unauthenticated_request_rejected(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        
        download_url = reverse('resume-download', kwargs={'pk': resume.id})
        response = self.client.get(download_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_19_analysis_can_be_linked_to_resume(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        analysis = ResumeAnalysis.objects.create(
            resume=resume,
            score=85.5,
            skills_found=['Python', 'Django'],
            strengths=['Good structure'],
            suggestions=['Add more projects']
        )
        self.assertEqual(ResumeAnalysis.objects.count(), 1)
        self.assertEqual(analysis.resume, resume)

    def test_20_student_can_view_own_analysis(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=85.5)
        
        self.client.force_authenticate(user=self.student_user)
        analysis_url = reverse('resume-analysis', kwargs={'pk': resume.id})
        response = self.client.get(analysis_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85.5)

    def test_21_student_cannot_view_another_students_analysis(self):
        other_resume = Resume.objects.create(student=self.student2, title='R_other', file=self.generate_pdf())
        from .models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=other_resume, score=90.0)
        
        self.client.force_authenticate(user=self.student_user)
        analysis_url = reverse('resume-analysis', kwargs={'pk': other_resume.id})
        response = self.client.get(analysis_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_22_latest_analysis_endpoint_returns_newest(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        import datetime
        from django.utils import timezone
        
        analysis1 = ResumeAnalysis.objects.create(resume=resume, score=70.0)
        ResumeAnalysis.objects.filter(id=analysis1.id).update(analyzed_at=timezone.now() - datetime.timedelta(days=1))
        
        ResumeAnalysis.objects.create(resume=resume, score=85.0)
        
        self.client.force_authenticate(user=self.student_user)
        analysis_url = reverse('resume-analysis', kwargs={'pk': resume.id})
        response = self.client.get(analysis_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85.0)

    def test_23_analysis_history_returns_multiple(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        import datetime
        from django.utils import timezone
        
        analysis1 = ResumeAnalysis.objects.create(resume=resume, score=70.0)
        ResumeAnalysis.objects.filter(id=analysis1.id).update(analyzed_at=timezone.now() - datetime.timedelta(days=1))
        
        ResumeAnalysis.objects.create(resume=resume, score=85.0)
        
        self.client.force_authenticate(user=self.student_user)
        analyses_url = reverse('resume-analyses', kwargs={'pk': resume.id})
        response = self.client.get(analyses_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['score'], 85.0)
        self.assertEqual(response.data[1]['score'], 70.0)

    def test_24_invalid_score_rejected(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            analysis = ResumeAnalysis(resume=resume, score=150.0)
            analysis.full_clean()

        with self.assertRaises(ValidationError):
            analysis = ResumeAnalysis(resume=resume, score=-10.0)
            analysis.full_clean()

    def test_25_unauthenticated_users_cannot_access_analysis(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from .models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=85.5)
        
        analysis_url = reverse('resume-analysis', kwargs={'pk': resume.id})
        response = self.client.get(analysis_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        analyses_url = reverse('resume-analyses', kwargs={'pk': resume.id})
        response2 = self.client.get(analyses_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
