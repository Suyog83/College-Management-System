from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from datetime import datetime
from .models import Student, Attendance, Course, ExamType, Exam, Marks
from .serializers import (
    LoginSerializer, StudentSerializer, AttendanceSerializer,
    AttendanceCreateSerializer, AttendanceReportSerializer
)
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def student_dashboard(request, student_id):
    """
    GET: Get student's attendance data for dashboard
    
    URL: /api/student-dashboard/<student_id>/
    Returns: Complete student dashboard with all attendance statistics
    """
    try:
        student = get_object_or_404(Student, id=student_id)
        
        # Get all attendance records for this student
        attendance_records = Attendance.objects.filter(
            student=student
        ).order_by('-date')
        
        # Calculate statistics
        total_classes = attendance_records.count()
        present_classes = attendance_records.filter(status='P').count()
        absent_classes = attendance_records.filter(status='A').count()
        
        if total_classes > 0:
            attendance_percentage = round((present_classes / total_classes) * 100)
        else:
            attendance_percentage = 0
        
        # Format attendance history
        attendance_history = []
        for record in attendance_records[:50]:  # Last 50 records
            attendance_history.append({
                'date': record.date.strftime('%B %d, %Y'),  # Format: January 06, 2024
                'status': record.status,
                'time': record.marked_at.strftime('%I:%M %p') if record.marked_at else 'N/A'
            })
        
        response_data = {
            'student_id': student.id,
            'student_name': student.name,
            'roll_number': student.roll_number,
            'total_classes': total_classes,
            'present_count': present_classes,
            'absent_count': absent_classes,
            'attendance_percentage': attendance_percentage,
            'attendance_history': attendance_history
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error in student_dashboard: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST: Authenticate user
    
    URL: /api/login/
    Body: {"id": "username", "password": "password"}
    Returns: User information with role and authentication details
    """
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid login request: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Invalid request data. Please provide both id and password.',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['id']
        password = serializer.validated_data['password']
        
        logger.info(f"Login attempt for username: {username}")
        
        # Try to authenticate as Django User first (for teachers/admin)
        # This takes priority over student login for security
        user = authenticate(username=username, password=password)
        
        if user:
            logger.info(f"User authenticated: {user.username}")
            # Determine user role
            role = None
            user_id = None
            user_name = None
            
            # Check if user is a teacher (has TeacherProfile)
            try:
                from .models import TeacherProfile
                teacher_profile = TeacherProfile.objects.get(user=user)
                role = 'teacher'
                # FIXED: Convert to string for consistency
                user_id = str(user.id)
                user_name = user.get_full_name() or user.username
                logger.info(f"User is a teacher: {user_name}")
            except TeacherProfile.DoesNotExist:
                # Check if user is staff (admin/teacher)
                if user.is_staff or user.is_superuser:
                    role = 'teacher'
                    # FIXED: Convert to string for consistency
                    user_id = str(user.id)
                    user_name = user.get_full_name() or user.username
                    logger.info(f"User is staff/teacher: {user_name}")
                else:
                    # Default to teacher for authenticated users
                    role = 'teacher'
                    # FIXED: Convert to string for consistency
                    user_id = str(user.id)
                    user_name = user.get_full_name() or user.username
                    logger.info(f"User authenticated as teacher (default): {user_name}")
            
            return Response({
                'success': True,
                'role': role,
                'user_id': user_id,
                'user_name': user_name,
                'message': 'Login successful',
                'token': None  # Can add JWT token here if needed
            }, status=status.HTTP_200_OK)
        
        # If Django User authentication failed, check if it's a student ID
        # (students can login with just their ID for demo purposes)
        try:
            student = Student.objects.get(id=username)
            logger.info(f"Found student: {student.name} (ID: {student.id})")
            # For demo: allow login with student ID and any password
            # In production, create User accounts for students
            return Response({
                'success': True,
                'role': 'student',
                'user_id': student.id,  # Already string (CharField)
                'user_name': student.name,
                'message': 'Login successful',
                'token': None
            }, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            logger.debug(f"Student with ID '{username}' not found")
            pass
        
        # Both authentication methods failed
        logger.warning(f"Authentication failed for username: {username}")
        
        # Check if username exists but password is wrong
        try:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                return Response({
                    'success': False,
                    'message': 'Invalid password. Please check your password.',
                    'error': 'The password you entered is incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}")
        
        return Response({
            'success': False,
            'message': 'Invalid credentials. Username not found. Please check your username and password, or run "python manage.py setup_default_users" to create default users.',
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'An error occurred during login. Please try again.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_students(request):
    """
    GET: Get list of all students
    
    URL: /api/students/
    Returns: List of all students
    """
    try:
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_students: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def mark_attendance(request):
    """
    POST: Mark attendance for students
    
    URL: /api/mark-attendance/
    Body: {"date": "2024-01-06", "records": [{"student_id": "Arjun-101", "status": "P"}, ...]}
    Returns: Created attendance records
    """
    try:
        serializer = AttendanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            records = serializer.validated_data['records']
            
            created_records = []
            for record_data in records:
                student_id = record_data['student_id']
                status_value = record_data['status']
                
                try:
                    student = Student.objects.get(id=student_id)
                    # Get or create attendance record (course can be None)
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        date=date,
                        course=None,  # Allow None for course
                        defaults={'status': status_value}
                    )
                    if not created:
                        attendance.status = status_value
                        attendance.save()
                    
                    created_records.append(AttendanceSerializer(attendance).data)
                except Student.DoesNotExist:
                    logger.warning(f"Student {student_id} not found")
                    continue
                except Exception as e:
                    logger.error(f"Error creating attendance for student {student_id}: {str(e)}")
                    continue
            
            return Response({
                'success': True,
                'message': f'Attendance marked for {len(created_records)} students',
                'records': created_records
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in mark_attendance: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendance_by_date(request, attendance_date):
    """
    GET: Get attendance records for a specific date
    
    URL: /api/attendance-by-date/<attendance_date>/
    Returns: List of attendance records for the date
    
    FIXED: Now returns actual attendance records instead of empty list
    """
    try:
        # Parse the date string
        date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        
        # Query attendance records for this date
        attendance_records = Attendance.objects.filter(
            date=date_obj
        ).select_related('student', 'course')
        
        # Serialize and return
        serializer = AttendanceSerializer(attendance_records, many=True)
        
        logger.info(f"Retrieved {len(attendance_records)} attendance records for {attendance_date}")
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in get_attendance_by_date: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def attendance_detail(request, student_id):
    """
    GET: Detailed attendance records for a student

    URL: /api/attendance-detail/<student_id>/
    """
    try:
        student = get_object_or_404(Student, id=student_id)
        records = (
            Attendance.objects.filter(student=student)
            .select_related('course')
            .order_by('-date')
        )
        serializer = AttendanceSerializer(records, many=True)
        return Response(
            {
                'student_id': student.id,
                'student_name': student.name,
                'records': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in attendance_detail: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def attendance_statistics(request, student_id):
    """
    GET: Summary statistics for a student's attendance

    URL: /api/attendance-statistics/<student_id>/
    """
    try:
        student = get_object_or_404(Student, id=student_id)
        qs = Attendance.objects.filter(student=student)
        total = qs.count()
        present = qs.filter(status='P').count()
        absent = qs.filter(status='A').count()
        percentage = round((present / total) * 100, 2) if total else 0

        return Response(
            {
                'student_id': student.id,
                'student_name': student.name,
                'total_classes': total,
                'present': present,
                'absent': absent,
                'attendance_percentage': percentage,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in attendance_statistics: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def teacher_attendance_summary(request):
    """
    GET: Attendance summary for all students (teacher view)

    URL: /api/teacher-attendance-summary/
    """
    try:
        students = Student.objects.all()
        summary = []
        for student in students:
            qs = Attendance.objects.filter(student=student)
            total = qs.count()
            present = qs.filter(status='P').count()
            absent = qs.filter(status='A').count()
            percentage = round((present / total) * 100, 2) if total else 0
            summary.append(
                {
                    'student_id': student.id,
                    'student_name': student.name,
                    'roll_number': student.roll_number,
                    'total_classes': total,
                    'present': present,
                    'absent': absent,
                    'attendance_percentage': percentage,
                }
            )
        return Response(summary, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in teacher_attendance_summary: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def attendance_by_date_range(request, student_id):
    """
    GET: Attendance records for a student within a date range.

    URL: /api/attendance-by-date-range/<student_id>/?start=YYYY-MM-DD&end=YYYY-MM-DD
    """
    try:
        student = get_object_or_404(Student, id=student_id)
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if not start or not end:
            return Response(
                {'error': 'start and end query params are required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()

        records = (
            Attendance.objects.filter(student=student, date__range=(start_date, end_date))
            .select_related('course')
            .order_by('-date')
        )
        serializer = AttendanceSerializer(records, many=True)
        return Response(
            {
                'student_id': student.id,
                'student_name': student.name,
                'start': start,
                'end': end,
                'records': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Error in attendance_by_date_range: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def attendance_report(request):
    """
    GET: Get attendance report
    
    URL: /api/attendance-report/?course=<course_id>&date=<date>
    Returns: Attendance report for course and date
    """
    try:
        course_id = request.query_params.get('course')
        date_str = request.query_params.get('date')
        
        if not course_id or not date_str:
            return Response(
                {'error': 'Both course and date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance_records = Attendance.objects.filter(
            course=course,
            date=date_obj
        )
        
        total_students = attendance_records.count()
        present = attendance_records.filter(status='P').count()
        absent = attendance_records.filter(status='A').count()
        present_percentage = (present / total_students * 100) if total_students > 0 else 0
        
        student_records = []
        for record in attendance_records:
            student_records.append({
                'student_id': record.student.id,
                'student_name': record.student.name,
                'roll_number': record.student.roll_number,
                'status': record.status
            })
        
        report_data = {
            'course': course.name,
            'date': date_str,
            'total_students': total_students,
            'present': present,
            'absent': absent,
            'present_percentage': round(present_percentage, 2),
            'student_records': student_records
        }
        
        return Response(report_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in attendance_report: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
 
# ==================== marks management ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_marks(request, student_id):
    """
    GET: Get all marks for a student
    
    URL: /api/marks/<student_id>/
    Returns: All marks across all exams and courses
    """
    try:
        student = get_object_or_404(Student, id=student_id)
        marks = (
            Marks.objects.filter(student=student)
            .select_related('exam', 'exam__course', 'exam__exam_type')
            .order_by('-created_at')
        )

        marks_data = []
        for mark in marks:
            marks_data.append({
                'id': mark.id,
                'course_id': mark.exam.course.id,
                'course_name': mark.exam.course.name,
                'exam_type': mark.exam.exam_type.name,
                'marks_obtained': float(mark.marks_obtained),
                'max_marks': float(mark.exam.max_marks),
                'percentage': float(mark.percentage) if mark.percentage is not None else 0,
                'grade': mark.grade,
            })
        
        return Response({
            'student_id': student.id,
            'student_name': student.name,
            'marks': marks_data
        }, status=status.HTTP_200_OK)
    
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_marks: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_marks(request):
    """
    POST: Upload/Update marks for students
    
    URL: /api/upload-marks/
    Body: {
        "course_id": "CS201",
        "exam_type": "midterm",
        "records": [
            {"student_id": "Arjun-101", "marks_obtained": 85, "max_marks": 100},
            ...
        ]
    }
    Returns: Created/Updated marks records
    """
    try:
        course_id = request.data.get('course_id')
        exam_type = request.data.get('exam_type')
        records = request.data.get('records', [])
        
        if not course_id or not exam_type or not records:
            return Response({
                'success': False,
                'error': 'course_id, exam_type, and records are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Course {course_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        created_records = []
        updated_count = 0

        # Ensure ExamType + Exam exist for this course/exam_type
        exam_type_obj, _ = ExamType.objects.get_or_create(
            name=str(exam_type).strip().title()
        )
        exam, _ = Exam.objects.get_or_create(
            course=course,
            exam_type=exam_type_obj,
            defaults={
                'name': f'{exam_type_obj.name} - {course.code}',
                'max_marks': 100,
            }
        )
        
        for record in records:
            student_id = record.get('student_id')
            marks_obtained = record.get('marks_obtained')
            max_marks = record.get('max_marks', 100)
            
            if not student_id or marks_obtained is None:
                continue
            
            try:
                student = Student.objects.get(id=student_id)

                # Update exam max marks for this upload batch
                try:
                    exam.max_marks = max_marks
                    exam.save()
                except Exception:
                    # Non-fatal; marks can still save
                    pass

                mark, created = Marks.objects.get_or_create(
                    student=student,
                    exam=exam,
                    defaults={'marks_obtained': marks_obtained},
                )
                
                if not created:
                    mark.marks_obtained = marks_obtained
                    mark.save()
                    updated_count += 1
                else:
                    created_records.append(mark)
                
            except Student.DoesNotExist:
                logger.warning(f"Student {student_id} not found")
                continue
            except Exception as e:
                logger.error(f"Error creating mark for student {student_id}: {str(e)}")
                continue
        
        return Response({
            'success': True,
            'message': f'Marks uploaded. Created: {len(created_records)}, Updated: {updated_count}',
            'created': len(created_records),
            'updated': updated_count
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error in upload_marks: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_course_marks(request, course_id):
    """
    GET: Get all marks for a course (teacher view)
    
    URL: /api/course-marks/<course_id>/
    Returns: All student marks in a course
    """
    try:
        course = get_object_or_404(Course, id=course_id)

        marks = (
            Marks.objects.filter(exam__course=course)
            .select_related('student', 'exam', 'exam__exam_type')
            .order_by('exam__exam_type__name', 'student__name')
        )

        # Group by exam type name
        marks_by_exam = {}
        for mark in marks:
            exam_type_name = mark.exam.exam_type.name
            if exam_type_name not in marks_by_exam:
                marks_by_exam[exam_type_name] = []

            marks_by_exam[exam_type_name].append({
                'student_id': mark.student.id,
                'student_name': mark.student.name,
                'roll_number': mark.student.roll_number,
                'marks_obtained': float(mark.marks_obtained),
                'max_marks': float(mark.exam.max_marks),
                'percentage': float(mark.percentage) if mark.percentage is not None else 0,
                'grade': mark.grade,
            })
        
        return Response({
            'course_id': course.id,
            'course_name': course.name,
            'marks_by_exam': marks_by_exam
        }, status=status.HTTP_200_OK)
    
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_course_marks: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_courses(request):
    """
    GET: Get all courses
    
    URL: /api/courses/
    Returns: List of all courses
    """
    try:
        courses = Course.objects.all()
        from .serializers import CourseSerializer
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_courses: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)