import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { AuthService } from '../services/auth.service';
import { HttpService } from '../services/http.service';

interface Student {
  id: string;
  name: string;
  roll_number?: string;
  status?: 'Present' | 'Absent';
}

interface ScheduleItem {
  time: string;
  subject: string;
  room: string;
  students: string;
}

interface Activity {
  action: string;
  subject: string;
  time: string;
  type: 'upload' | 'attendance' | 'assignment';
}

interface StudentMark {
  student_id: string;
  student_name: string;
  roll_number?: string;
  marks_obtained: number;
  max_marks: number;
  percentage: number;
  grade: string;
}

@Component({
  selector: 'app-teacher-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatSelectModule
  ],
  templateUrl: './teacher-dashboard.html',
  styleUrl: './teacher-dashboard.css'
})
export class TeacherDashboard implements OnInit {
  authService = inject(AuthService);
  private httpService = inject(HttpService);

  // Navigation
  toggleSidebar(){
    this.sidebarOpen.update(val => !val);
  }
  activeTab = signal<'dashboard' | 'attendance' | 'marks'>('dashboard');
  switchTab(tab: 'dashboard' | 'attendance' | 'marks') {
    this.activeTab.set(tab);
  }
  sidebarOpen = signal(true);

  // Dashboard data
  students = signal<Student[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  success = signal<string | null>(null);

  // MatTable configuration
  displayedColumns: string[] = ['srno', 'rollNo', 'name', 'status', 'action'];
  dataSource = new MatTableDataSource<Student>();
  pageSize = signal(10);
  pageSizeOptions = [5, 10, 25, 50];

  // Attendance form data
  selectedCourse = signal('Data Structures (CS201)');
  selectedDate = signal(this.getTodayDate());
  
  getTodayDate(): string {
    return new Date().toISOString().split('T')[0];
  }

  onDateChange() {
    this.loadStudents();
  }

  attendanceStudents = signal<Student[]>([]);

  // Marks form data
  selectedCourseMarks = signal('Data Structures (CS201)');
  selectedExamType = signal('midterm');
  studentMarks = signal<StudentMark[]>([]);
  marksLoading = signal(false);
  marksDataSource = new MatTableDataSource<StudentMark>();
  marksDisplayedColumns: string[] = ['rollNo', 'name', 'marksObtained', 'maxMarks', 'percentage', 'grade'];
  marksPageSize = signal(10);

  stats = signal([
    { 
      icon: 'courses', 
      label: 'My Courses', 
      value: '5', 
      color: 'bg-blue-500' 
    },
    { 
      icon: 'students', 
      label: 'Total Students', 
      value: '10', 
      color: 'bg-green-500' 
    },
    { 
      icon: 'classes', 
      label: 'Classes Today', 
      value: '3', 
      color: 'bg-purple-500' 
    },
    { 
      icon: 'evaluations', 
      label: 'Pending Evaluations', 
      value: '12', 
      color: 'bg-orange-500' 
    },
  ]);

  courses = [
    'Data Structures (CS201)',
    'Algorithms (CS205)',
    'Database Design (CS210)',
    'Web Development (CS215)',
    'Machine Learning (CS220)'
  ];

  examTypes = [
    { value: 'midterm', label: 'Midterm Exam' },
    { value: 'final', label: 'Final Exam' },
    { value: 'quiz', label: 'Quiz' },
    { value: 'assignment', label: 'Assignment' }
  ];

  schedule: ScheduleItem[] = [
    { time: '09:00 AM', subject: 'Data Structures', room: 'Room 201', students: '45 students' },
    { time: '11:00 AM', subject: 'Algorithms', room: 'Room 305', students: '38 students' },
    { time: '02:00 PM', subject: 'Database Design', room: 'Room 202', students: '42 students' },
  ];

  activities: Activity[] = [
    { action: 'Uploaded marks for Midterm Exam', subject: 'Data Structures', time: '2 hours ago', type: 'upload' },
    { action: 'Marked attendance for morning class', subject: 'Algorithms', time: '3 hours ago', type: 'attendance' },
    { action: 'Created new assignment', subject: 'Database Design', time: '5 hours ago', type: 'assignment' },
  ];

  ngOnInit() {
    this.loadStudents();
    this.initializeMarks();
  }

  loadStudents() {
    this.loading.set(true);
    this.error.set(null);

    this.httpService.getStudents().subscribe({
      next: (response) => {
        const studentsList: Student[] = response.map((s: any) => ({
          id: s.id,
          name: s.name,
          roll_number: s.roll_number,
          status: 'Present' as const
        }));
        this.students.set(studentsList);

        const selectedDate = this.selectedDate();
        
        this.httpService.getAttendanceByDate(selectedDate).subscribe({
          next: (attendanceRecords) => {
            const attendanceMap = new Map<string, 'Present' | 'Absent'>();
            
            attendanceRecords.forEach((record: any) => {
              const status = record.status === 'P' ? 'Present' : 'Absent';
              if (record.student) {
                attendanceMap.set(record.student, status);
              }
            });

            const studentsWithAttendance = studentsList.map(student => ({
              ...student,
              status: attendanceMap.has(student.id) 
                ? attendanceMap.get(student.id)! 
                : 'Present' as const
            }));

            this.attendanceStudents.set(studentsWithAttendance);
            this.dataSource.data = studentsWithAttendance;

            const updatedStats = this.stats().map(stat =>
              stat.label === 'Total Students' ? { ...stat, value: studentsList.length.toString() } : stat
            );
            this.stats.set(updatedStats);
            this.loading.set(false);
          },
          error: (attendanceErr) => {
            console.log('No attendance found for date, using defaults');
            this.attendanceStudents.set(studentsList);
            this.dataSource.data = studentsList;
            
            const updatedStats = this.stats().map(stat =>
              stat.label === 'Total Students' ? { ...stat, value: studentsList.length.toString() } : stat
            );
            this.stats.set(updatedStats);
            this.loading.set(false);
          }
        });
      },
      error: (err) => {
        this.error.set('Failed to load students. Make sure the backend is running.');
        console.error('Error loading students:', err);
        this.loading.set(false);
      }
    });
  }

  // Apply filter for table search
  applyFilter(event: any) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  applyMarksFilter(event: any) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.marksDataSource.filter = filterValue.trim().toLowerCase();
  }

  // Marks Methods
  initializeMarks() {
    const students = this.students();
    const marksData: StudentMark[] = students.map(student => ({
      student_id: student.id,
      student_name: student.name,
      roll_number: student.roll_number,
      marks_obtained: 0,
      max_marks: 100,
      percentage: 0,
      grade: '-'
    }));
    this.studentMarks.set(marksData);
    this.marksDataSource.data = marksData;
  }

  updateMarks(studentId: string, marksObtained: number) {
    this.studentMarks.update(marks =>
      marks.map(mark => {
        if (mark.student_id === studentId) {
          const percentage = (marksObtained / mark.max_marks) * 100;
          let grade = '-';
          
          if (percentage >= 90) grade = 'A+';
          else if (percentage >= 85) grade = 'A';
          else if (percentage >= 80) grade = 'B+';
          else if (percentage >= 75) grade = 'B';
          else if (percentage >= 70) grade = 'C+';
          else if (percentage >= 60) grade = 'C';
          else if (percentage >= 50) grade = 'D';
          else grade = 'F';
          
          return {
            ...mark,
            marks_obtained: marksObtained,
            percentage: Math.round(percentage),
            grade: grade
          };
        }
        return mark;
      })
    );
    this.marksDataSource.data = [...this.studentMarks()];
  }

  getAverageMarks(): number {
    const marks = this.studentMarks();
    if (marks.length === 0) return 0;
    const total = marks.reduce((sum, mark) => sum + mark.marks_obtained, 0);
    return Math.round(total / marks.length);
  }

  saveMarks() {
    const marksToUpload = this.studentMarks()
      .filter(m => m.marks_obtained > 0)
      .map(m => ({
        student_id: m.student_id,
        marks_obtained: m.marks_obtained,
        max_marks: m.max_marks
      }));

    if (marksToUpload.length === 0) {
      this.error.set('Please enter marks for at least one student');
      return;
    }

    this.marksLoading.set(true);
    this.error.set(null);
    this.success.set(null);

    const payload = {
      course_id: this.selectedCourseMarks().split('(')[1].split(')')[0],
      exam_type: this.selectedExamType(),
      records: marksToUpload
    };

    this.httpService.uploadMarks(payload).subscribe({
      next: (response) => {
        this.success.set(`Marks saved successfully! Created: ${response.created}, Updated: ${response.updated}`);
        this.marksLoading.set(false);
        
        setTimeout(() => {
          this.success.set(null);
        }, 5000);
      },
      error: (err) => {
        this.error.set('Failed to save marks. Please try again.');
        console.error('Error saving marks:', err);
        this.marksLoading.set(false);
      }
    });
  }

  toggleStatus(id: string) {
    this.attendanceStudents.update(students =>
      students.map(student =>
        student.id === id
          ? { ...student, status: student.status === 'Present' ? 'Absent' : 'Present' }
          : student
      )
    );
    this.dataSource.data = [...this.attendanceStudents()];
  }

  presentCount = computed(() => {
    return this.attendanceStudents().filter(s => s.status === 'Present').length;
  })
  
  absentCount = computed(() => {
    return this.attendanceStudents().filter(s => s.status === 'Absent').length;
  })

  saveAttendance() {
    if (this.attendanceStudents().length === 0) {
      this.error.set('No students to mark attendance for');
      return;
    }
  
    this.loading.set(true);
    this.error.set(null);
    this.success.set(null);

    const records = this.attendanceStudents()
      .filter(s => s.status === 'Present' || s.status === 'Absent')
      .map(s => ({
        student_id: s.id,
        status: s.status === 'Present' ? 'P' : 'A' as 'P' | 'A'
      }));

    const attendanceData = {
      date: this.selectedDate(),
      records: records
    };

    this.httpService.markAttendance(attendanceData).subscribe({
      next: (response) => {
        this.success.set(response.message || `Attendance marked successfully for ${records.length} students`);
        this.loading.set(false);
        
        setTimeout(() => {
          this.success.set(null);
        }, 5000);
        
        this.loadStudents();
      },
      error: (err) => {
        const errorMessage = err.error?.message || err.error?.error || 'Failed to mark attendance. Please try again.';
        this.error.set(errorMessage);
        console.error('Error marking attendance:', err);
        this.loading.set(false);
      }
    });
  }
}