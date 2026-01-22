from django.core.management.base import BaseCommand
from api.models import Student

class Command(BaseCommand):
    help = 'Populate database with sample students'

    def handle(self, *args, **options):
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

        for data in students_data:
            student, created = Student.objects.get_or_create(
                id=data['id'],
                defaults={
                    'name': data['name'],
                    'roll_number': data['roll_number']
                }
            )
            if created:
                self.stdout.write(f'Created: {student.name}')
            else:
                self.stdout.write(f'Already exists: {student.name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated students'))