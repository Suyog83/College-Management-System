from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('login/', views.login, name='login'),
    
    # Student endpoints
    path('students/', views.get_students, name='get_students'),
    path('courses/', views.get_courses, name='get_courses'),
    
    # Attendance marking
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Student dashboard
    path('student-dashboard/<str:student_id>/', views.student_dashboard, name='student_dashboard'),
    
    # Attendance by date
    path('attendance-by-date/<str:attendance_date>/', views.get_attendance_by_date, name='attendance_by_date'),
    
    # Attendance detail view
    path('attendance-detail/<str:student_id>/', views.attendance_detail, name='attendance_detail'),
    
    # Attendance statistics
    path('attendance-statistics/<str:student_id>/', views.attendance_statistics, name='attendance_statistics'),
    
    # Teacher attendance summary (all students)
    path('teacher-attendance-summary/', views.teacher_attendance_summary, name='teacher_attendance_summary'),
    
    # Attendance by date range
    path('attendance-by-date-range/<str:student_id>/', views.attendance_by_date_range, name='attendance_by_date_range'),
    
    # Attendance report
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    
    # Marks endpoints
    path('marks/<str:student_id>/', views.get_marks, name='get_marks'),
    path('upload-marks/', views.upload_marks, name='upload_marks'),
    path('course-marks/<str:course_id>/', views.get_course_marks, name='get_course_marks'),
]