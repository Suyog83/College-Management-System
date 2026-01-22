from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Course, Attendance, AttendanceSession, TeacherProfile


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    id = serializers.CharField()
    password = serializers.CharField(write_only=True)


class StudentSerializer(serializers.ModelSerializer):
    """Serialize student data"""
    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_number', 'email', 'phone', 'created_at']
        read_only_fields = ['created_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    """Detailed student serializer with attendance stats"""
    attendance_count = serializers.SerializerMethodField()
    present_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_number', 'email', 'phone', 'attendance_count', 'present_count']

    def get_attendance_count(self, obj):
        return obj.attendance_records.count()

    def get_present_count(self, obj):
        return obj.attendance_records.filter(status='P').count()


class CourseSerializer(serializers.ModelSerializer):
    """Serialize course data"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'teacher', 'created_at']
        read_only_fields = ['created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    """Serialize attendance records"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True, required=False)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_name',
            'student_roll',
            'course',
            'course_name',
            'date',
            'status',
            'marked_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'marked_at']


class AttendanceCreateSerializer(serializers.Serializer):
    """Serializer for bulk attendance creation"""
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

    def validate(self, attrs):
        """Validate attendance data"""
        if not attrs.get('records'):
            raise serializers.ValidationError("Records list cannot be empty")
        
        for record in attrs['records']:
            if 'student_id' not in record or 'status' not in record:
                raise serializers.ValidationError(
                    "Each record must have 'student_id' and 'status'"
                )
            if record['status'] not in ['P', 'A']:
                raise serializers.ValidationError(
                    f"Status must be 'P' or 'A', got {record['status']}"
                )
        
        return attrs


class AttendanceHistorySerializer(serializers.Serializer):
    """Serializer for attendance history display"""
    date = serializers.DateField()
    status = serializers.CharField()
    time = serializers.SerializerMethodField()

    def get_time(self, obj):
        if hasattr(obj, 'marked_at') and obj.marked_at:
            return obj.marked_at.strftime('%I:%M %p')
        return 'N/A'


class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard data"""
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    roll_number = serializers.CharField()
    total_classes = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    attendance_percentage = serializers.IntegerField()
    attendance_history = serializers.ListField(
        child=serializers.DictField()
    )


class AttendanceSessionSerializer(serializers.ModelSerializer):
    """Serialize attendance session data"""
    class Meta:
        model = AttendanceSession
        fields = [
            'id',
            'course',
            'date',
            'teacher',
            'total_students',
            'present_count',
            'absent_count',
            'created_at'
        ]
        read_only_fields = ['created_at']


class AttendanceReportSerializer(serializers.Serializer):
    """Serializer for attendance report"""
    course = serializers.CharField()
    date = serializers.DateField()
    total_students = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    present_percentage = serializers.FloatField()
    student_records = serializers.ListField(
        child=serializers.DictField()
    )


class UserSerializer(serializers.ModelSerializer):
    """Serialize User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serialize teacher profile"""
    user = UserSerializer()

    class Meta:
        model = TeacherProfile
        fields = ['user', 'employee_id', 'subject']