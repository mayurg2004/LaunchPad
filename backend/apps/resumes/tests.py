import io
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, UserRole
from students.models import Student
from resumes.models import Resume

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
        self.assertIn('mydoc', response['Content-Disposition'])
        self.assertIn('.pdf', response['Content-Disposition'])

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
        from resumes.models import ResumeAnalysis
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
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=85.5)
        
        self.client.force_authenticate(user=self.student_user)
        analysis_url = reverse('resume-analysis', kwargs={'pk': resume.id})
        response = self.client.get(analysis_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85.5)

    def test_21_student_cannot_view_another_students_analysis(self):
        other_resume = Resume.objects.create(student=self.student2, title='R_other', file=self.generate_pdf())
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=other_resume, score=90.0)
        
        self.client.force_authenticate(user=self.student_user)
        analysis_url = reverse('resume-analysis', kwargs={'pk': other_resume.id})
        response = self.client.get(analysis_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_22_latest_analysis_endpoint_returns_newest(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from resumes.models import ResumeAnalysis
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
        from resumes.models import ResumeAnalysis
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
        from resumes.models import ResumeAnalysis
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            analysis = ResumeAnalysis(resume=resume, score=150.0)
            analysis.full_clean()

        with self.assertRaises(ValidationError):
            analysis = ResumeAnalysis(resume=resume, score=-10.0)
            analysis.full_clean()

    def test_25_unauthenticated_users_cannot_access_analysis(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=85.5)
        
        analysis_url = reverse('resume-analysis', kwargs={'pk': resume.id})
        response = self.client.get(analysis_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        analyses_url = reverse('resume-analyses', kwargs={'pk': resume.id})
        response2 = self.client.get(analyses_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def generate_valid_pdf(self, name='valid.pdf'):
        # Minimal valid PDF string
        minimal_pdf = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF\n"
        return SimpleUploadedFile(name, minimal_pdf, content_type='application/pdf')

    def test_26_analyze_endpoint_requires_auth(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_27_student_can_analyze_own_pdf_valid(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("resume_id", response.data)
        self.assertIn("skills_found", response.data)
        self.assertIn("analyzed_at", response.data)
        self.assertNotIn("text", response.data)

    def test_28_student_cannot_analyze_another_students_pdf(self):
        other_resume = Resume.objects.create(student=self.student2, title='R_other', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': other_resume.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_29_analyze_invalid_pdf_handled(self):
        # generate_pdf returns b'a' * size which is not a valid PDF
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf('invalid.pdf'))
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Invalid or unreadable PDF file.")

    def test_30_missing_resume_file_handled(self):
        resume = Resume.objects.create(student=self.student, title='R1')
        # Manually remove file to simulate missing
        resume.file = None
        resume.save()
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "File not found.")

    @patch('resumes.utils.extract_text_from_pdf')
    def test_31_analyze_multiple_skills_detected(self, mock_extract):
        mock_extract.return_value = "I have experience with Python, Java, and React."
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("resume_id", response.data)
        self.assertIn("Python", response.data['skills_found'])
        self.assertIn("Java", response.data['skills_found'])
        self.assertIn("React", response.data['skills_found'])
        self.assertEqual(len(response.data['skills_found']), 3)
        self.assertNotIn("text", response.data)
        
        # Check that it's stored in the database
        from resumes.models import ResumeAnalysis
        analysis = ResumeAnalysis.objects.get(resume=resume)
        self.assertEqual(analysis.score, 29.0)
        self.assertIn("Python", analysis.skills_found)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_32_analyze_case_insensitive_matching(self, mock_extract):
        mock_extract.return_value = "Skilled in jAvA, HTML, css, and node.js!"
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Java", response.data['skills_found'])
        self.assertIn("HTML", response.data['skills_found'])
        self.assertIn("CSS", response.data['skills_found'])
        self.assertIn("Node.js", response.data['skills_found'])
        self.assertEqual(len(response.data['skills_found']), 4)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_33_analyze_no_matching_skills(self, mock_extract):
        mock_extract.return_value = "I am a very good team player who works hard."
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skills_found'], [])
        
        from resumes.models import ResumeAnalysis
        analysis = ResumeAnalysis.objects.get(resume=resume)
        self.assertEqual(analysis.skills_found, [])

    @patch('resumes.utils.extract_text_from_pdf')
    def test_34_analyze_comprehensive_score(self, mock_extract):
        mock_extract.return_value = (
            "Education and work history.\n"
            "Skills include Java, Python, SQL, Git, AWS.\n"
            "Contact: john.doe@email.com, +1 555 1234567\n"
            "Check out my projects on github.com and my portfolio.\n"
            "Achievements and Certifications are great."
        )
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Skills: 5 * 8 = 40
        # Sections: education, work history, skills, contact, projects, achievements, certifications (max 30)
        # Contact: email (5) + phone (5) = 10
        # Links: github.com (4) + portfolio (2) = 6
        # Length: < 500 = 0
        # Total = 40 + 30 + 10 + 6 = 86
        self.assertEqual(response.data['score'], 86.0)
        
        # Test capping at 100
        # Add length > 1000 = 10 points, and another link (linkedin = 4 points)
        # 86 + 14 = 100.
        mock_extract.return_value += " linkedin.com " + "A" * 1500
        
        url2 = reverse('resume-analyze', kwargs={'pk': resume.id})
        response2 = self.client.post(url2)
        self.assertEqual(response2.data['score'], 100.0)

    def create_placement_drive(self, required_skills):
        from companies.models import Company
        from placement_drive.models import PlacementDrive
        
        company = Company.objects.create(company_name='C2', industry='IT', website='b.com')
        drive = PlacementDrive.objects.create(
            company=company, title='D1', job_role='R1', required_skills=required_skills
        )
        return drive

    def test_35_skill_gap_all_skills_matched(self):
        resume = Resume.objects.create(student=self.student, title='R1')
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=50.0, skills_found=["Python", "Django", "SQL"])
        
        drive = self.create_placement_drive(["Python", "Django"])
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-skill-gap', kwargs={'pk': resume.id, 'drive_id': drive.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['match_percentage'], 100.0)
        self.assertEqual(len(response.data['matched_skills']), 2)
        self.assertEqual(len(response.data['missing_skills']), 0)
        
    def test_36_skill_gap_some_skills_matched(self):
        resume = Resume.objects.create(student=self.student, title='R1')
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=50.0, skills_found=["Python", "SQL"])
        
        drive = self.create_placement_drive(["Python", "Django", "React"])
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-skill-gap', kwargs={'pk': resume.id, 'drive_id': drive.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Match percentage = (1 / 3) * 100 = 33.33
        self.assertEqual(response.data['match_percentage'], 33.33)
        self.assertEqual(response.data['matched_skills'], ["Python"])
        self.assertEqual(response.data['missing_skills'], ["Django", "React"])

    def test_37_skill_gap_case_insensitive_matching(self):
        resume = Resume.objects.create(student=self.student, title='R1')
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=50.0, skills_found=["python", "REACT"])
        
        drive = self.create_placement_drive(["PYTHON", "react"])
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-skill-gap', kwargs={'pk': resume.id, 'drive_id': drive.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['match_percentage'], 100.0)
        self.assertIn("PYTHON", response.data['matched_skills'])
        self.assertIn("react", response.data['matched_skills'])

    def test_38_skill_gap_no_required_skills(self):
        resume = Resume.objects.create(student=self.student, title='R1')
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=50.0, skills_found=["Python"])
        
        drive = self.create_placement_drive([])
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-skill-gap', kwargs={'pk': resume.id, 'drive_id': drive.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['match_percentage'], 100.0)

    def test_39_skill_gap_unauthorized_and_invalid_drive(self):
        # Invalid drive
        resume = Resume.objects.create(student=self.student, title='R1')
        from resumes.models import ResumeAnalysis
        ResumeAnalysis.objects.create(resume=resume, score=50.0, skills_found=[])
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-skill-gap', kwargs={'pk': resume.id, 'drive_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Unauthorized access to another student's resume
        drive = self.create_placement_drive(["Java"])
        other_resume = Resume.objects.create(student=self.student2, title='R2')
        url2 = reverse('resume-skill-gap', kwargs={'pk': other_resume.id, 'drive_id': drive.id})
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        
        # Missing resume analysis
        no_analysis_resume = Resume.objects.create(student=self.student, title='R3')
        url3 = reverse('resume-skill-gap', kwargs={'pk': no_analysis_resume.id, 'drive_id': drive.id})
        response3 = self.client.get(url3)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_40_analyze_generates_suggestions_for_missing_sections(self, mock_extract):
        mock_extract.return_value = "Just some text with no sections."
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suggestions = response.data['suggestions']
        self.assertIn("Consider adding an education section to highlight your academic background.", suggestions)
        self.assertIn("Consider adding 2-3 relevant academic or personal projects.", suggestions)
        self.assertIn("Consider adding a professional email address.", suggestions)
        self.assertIn("Consider adding your GitHub or LinkedIn profile.", suggestions)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_41_analyze_does_not_generate_missing_for_existing_sections(self, mock_extract):
        mock_extract.return_value = (
            "Education section here.\n"
            "Experience and Work history.\n"
            "Projects are listed.\n"
            "Certifications are included.\n"
            "Skills: Java, Python.\n"
            "Contact: test@email.com, +1 555 1234567\n"
            "Links: github.com\n"
            "Achievements section."
        )
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suggestions = response.data['suggestions']
        self.assertNotIn("Consider adding an education section to highlight your academic background.", suggestions)
        self.assertNotIn("Consider adding 2-3 relevant academic or personal projects.", suggestions)
        self.assertNotIn("Consider adding a professional email address.", suggestions)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_42_analyze_generates_strengths_correctly(self, mock_extract):
        mock_extract.return_value = (
            "Projects are listed.\n"
            "Certifications are included.\n"
            "Skills: Python, Java, React, SQL, AWS.\n"
            "Links: github.com"
        )
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        strengths = response.data['strengths']
        self.assertIn("Good project section.", strengths)
        self.assertIn("Multiple relevant certifications.", strengths)
        self.assertIn("GitHub profile available.", strengths)
        self.assertIn("Strong technical skill coverage.", strengths)

    @patch('resumes.utils.extract_text_from_pdf')
    def test_43_suggestions_are_stored_in_resume_analysis(self, mock_extract):
        mock_extract.return_value = "Empty."
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        self.client.post(url)
        
        from .models import ResumeAnalysis
        analysis = ResumeAnalysis.objects.get(resume=resume)
        self.assertTrue(len(analysis.suggestions) > 0)
        self.assertIn("Consider adding an education section to highlight your academic background.", analysis.suggestions)
        
    @patch('resumes.utils.extract_text_from_pdf')
    def test_44_verify_existing_functionality_works_with_feedback(self, mock_extract):
        mock_extract.return_value = "Python, Java, Git"
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_valid_pdf())
        self.client.force_authenticate(user=self.student_user)
        url = reverse('resume-analyze', kwargs={'pk': resume.id})
        response = self.client.post(url)
        
        # Test old functionality
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Python", response.data['skills_found'])
        self.assertIn("Java", response.data['skills_found'])
        self.assertIn("Git", response.data['skills_found'])
        self.assertTrue(response.data['score'] > 0)
        
        # Test new fields are present
        self.assertIn("strengths", response.data)
        self.assertIn("suggestions", response.data)

