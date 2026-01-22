from django.db import models
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

class Student(models.Model):
    """Student model with roll number and basic info"""
    id = models.CharField(max_length=20, primary_key=True, unique=True)  # e.g., "Arjun-101"
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.name} ({self.id})"


class Course(models.Model):
    """Course model"""
    id = models.CharField(max_length=20, primary_key=True)  # e.g., "CS201"
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    credits = models.IntegerField(default=3)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Attendance(models.Model):
    """Attendance record model"""
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    marked_at = models.TimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date', 'course')
        ordering = ['-date']
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


class AttendanceSession(models.Model):
    """Attendance session for bulk operations"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_students = models.IntegerField(default=0, null=True, blank=True)
    present_count = models.IntegerField(default=0, null=True, blank=True)
    absent_count = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.course} - {self.date}"

    def calculate_stats(self):
        """Calculate attendance statistics"""
        attendance = Attendance.objects.filter(
            course=self.course,
            date=self.date
        )
        self.total_students = attendance.count()
        self.present_count = attendance.filter(status='P').count()
        self.absent_count = attendance.filter(status='A').count()
        self.save()


class TeacherProfile(models.Model):
    """Teacher profile linked to User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()}"


# ==================== NEW MODELS FOR MARKS MANAGEMENT ====================

class ExamType(models.Model):
    """Exam types like Midterm, Final, Assignment, etc."""
    name = models.CharField(max_length=50, unique=True)  # e.g., "Midterm Exam", "Final Exam"
    weightage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage weightage
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.weightage}%)"


class Exam(models.Model):
    """Specific exam instance"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., "Midterm Exam - Semester 1"
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    date = models.DateField(null=True, blank=True)
    semester = models.CharField(max_length=20, default='Current Semester')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('course', 'exam_type', 'semester')

    def __str__(self):
        return f"{self.course.code} - {self.exam_type.name}"


class Marks(models.Model):
    """Student marks for exams"""
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'),
        ('A', 'A (85-89)'),
        ('A-', 'A- (80-84)'),
        ('B+', 'B+ (75-79)'),
        ('B', 'B (70-74)'),
        ('B-', 'B- (65-69)'),
        ('C+', 'C+ (60-64)'),
        ('C', 'C (55-59)'),
        ('C-', 'C- (50-54)'),
        ('D', 'D (40-49)'),
        ('F', 'F (0-39)'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_marks')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'exam')
        verbose_name_plural = "Marks"

    def __str__(self):
        return f"{self.student.name} - {self.exam.name} - {self.marks_obtained}/{self.exam.max_marks}"

    def save(self, *args, **kwargs):
        """Calculate percentage and grade before saving"""
        if self.marks_obtained is not None and self.exam.max_marks:
            self.percentage = (self.marks_obtained / self.exam.max_marks) * 100
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

    def calculate_grade(self):
        """Calculate letter grade based on percentage"""
        if self.percentage is None:
            return 'F'
        
        if self.percentage >= 90:
            return 'A+'
        elif self.percentage >= 85:
            return 'A'
        elif self.percentage >= 80:
            return 'A-'
        elif self.percentage >= 75:
            return 'B+'
        elif self.percentage >= 70:
            return 'B'
        elif self.percentage >= 65:
            return 'B-'
        elif self.percentage >= 60:
            return 'C+'
        elif self.percentage >= 55:
            return 'C'
        elif self.percentage >= 50:
            return 'C-'
        elif self.percentage >= 40:
            return 'D'
        else:
            return 'F'

    def get_grade_point(self):
        """Get grade point for GPA calculation"""
        grade_points = {
            'A+': 4.0, 'A': 3.7, 'A-': 3.3,
            'B+': 3.0, 'B': 2.7, 'B-': 2.3,
            'C+': 2.0, 'C': 1.7, 'C-': 1.3,
            'D': 1.0, 'F': 0.0
        }
        return grade_points.get(self.grade, 0.0)