from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Student, TeacherProfile

class Command(BaseCommand):
    help = 'Setup default admin user and populate students'

    def handle(self, *args, **options):
        # Create default admin/teacher user
        admin_username = 'admin'
        admin_password = 'teacher123'
        
        user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': 'admin@school.com',
                'first_name': 'Admin',
                'last_name': 'Teacher',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password(admin_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_username} / {admin_password}'))
        else:
            # Update password if user exists
            user.set_password(admin_password)
            user.save()
            self.stdout.write(self.style.WARNING(f'Updated password for existing admin user: {admin_username} / {admin_password}'))
        
        # Create TeacherProfile for admin
        teacher_profile, created = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': 'T001',
                'subject': 'Administration'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created teacher profile for admin'))
        
        # Populate students
        students_data = [
            {'id': 'Arjun-101', 'name': 'Arjun Mehta', 'roll_number': '101'},
            {'id': 'Sana-102', 'name': 'Sana Khan', 'roll_number': '102'},
            {'id': 'Rahul-103', 'name': 'Rahul Sharma', 'roll_number': '103'},
            {'id': 'Priya-104', 'name': 'Priya Verma', 'roll_number': '104'},
            {'id': 'Amit-105', 'name': 'Amit Singh', 'roll_number': '105'},
            {'id': 'Sneha-106', 'name': 'Sneha Patil', 'roll_number': '106'},
            {'id': 'Rohan-107', 'name': 'Rohan Das', 'roll_number': '107'},
            {'id': 'Neha-108', 'name': 'Neha Gupta', 'roll_number': '108'},
            {'id': 'Vikram-109', 'name': 'Vikram Rathore', 'roll_number': '109'},
            {'id': 'Anjali-110', 'name': 'Anjali Nair', 'roll_number': '110'},
        ]

        created_count = 0
        for data in students_data:
            student, created = Student.objects.get_or_create(
                id=data['id'],
                defaults={
                    'name': data['name'],
                    'roll_number': data['roll_number']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {student.name} (ID: {student.id})')
            else:
                self.stdout.write(f'Already exists: {student.name} (ID: {student.id})')

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully setup default users and {created_count} new students'))
        self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
        self.stdout.write(self.style.SUCCESS(f'  Teacher: {admin_username} / {admin_password}'))
        self.stdout.write(self.style.SUCCESS(f'  Student: Arjun-101 / (any password)'))

