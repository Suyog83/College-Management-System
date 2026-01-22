from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Course, Attendance, AttendanceSession, TeacherProfile


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = ['id', 'name', 'roll_number', 'email', 'attendance_count', 'created_at']
    search_fields = ['name', 'id', 'roll_number', 'email']
    list_filter = ['created_at']
    ordering = ['roll_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'name', 'roll_number', 'email', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def attendance_count(self, obj):
        count = obj.attendance_records.count()
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    attendance_count.__name__= 'Attendance Records'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""
    list_display = ['id', 'name', 'code', 'teacher', 'created_at']
    search_fields = ['name', 'code', 'id']
    list_filter = ['created_at', 'teacher']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('id', 'name', 'code', 'teacher')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance model"""
    list_display = ['student', 'date', 'status_badge', 'marked_at', 'course']
    search_fields = ['student__name', 'student__id', 'date']
    list_filter = ['date', 'status', 'course', 'created_at']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at', 'marked_at']
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'course', 'date', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'marked_by')
        }),
        ('Timestamps', {
            'fields': ('marked_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        if obj.status == 'P':
            color = '#4CAF50'
            label = 'PRESENT'
        else:
            color = '#f44336'
            label = 'ABSENT'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color, label
        )
    status_badge.__name__ = 'Status'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'course')


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceSession model"""
    list_display = ['course', 'date', 'teacher', 'present_count', 'absent_count', 'total_students']
    search_fields = ['course__name', 'date']
    list_filter = ['date', 'course', 'teacher', 'created_at']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at', 'total_students', 'present_count', 'absent_count']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('course', 'date', 'teacher')
        }),
        ('Statistics', {
            'fields': ('total_students', 'present_count', 'absent_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['calculate_stats_action']
    
    def calculate_stats_action(self, request, queryset):
        """Admin action to recalculate statistics"""
        count = 0
        for session in queryset:
            session.calculate_stats()
            count += 1
        self.message_user(request, f'Calculated stats for {count} sessions')
    calculate_stats_action.__name__ = 'Recalculate statistics for selected sessions'


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin interface for TeacherProfile model"""
    list_display = ['user', 'employee_id', 'subject', 'created_at']
    search_fields = ['user__username', 'employee_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Teacher Information', {
            'fields': ('user', 'employee_id', 'subject')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )