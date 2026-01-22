import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { HttpService } from '../services/http.service';

interface AttendanceRecord {
  date: string;
  time: string;
  status: 'P' | 'A';
}

interface StudentDashboardResponse {
  student_id: string;
  student_name: string;
  roll_number: string;
  total_classes?: number;
  present_count?: number;
  absent_count?: number;
  attendance_percentage: number;
  attendance_history: AttendanceRecord[];
}

@Component({
  selector: 'app-student-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './student-dashboard.html',
  styleUrl: './student-dashboard.css',
})
export class StudentDashboard implements OnInit {
  authService = inject(AuthService);
  private httpService = inject(HttpService);

  // Student Profile Data
  studentName = signal<string | null>(null);
  studentId = signal<string | null>(null);
  rollNumber = signal<string | null>(null);

  // Attendance Stats
  totalClasses = signal(0);
  presentCount = signal(0);
  absentCount = signal(0);
  attendancePercentage = signal(0);
  attendanceHistory = signal<AttendanceRecord[]>([]);

  // UI States
  loading = signal(false);
  error = signal<string | null>(null);
  sidebarOpen = signal(false);

  ngOnInit() {
    this.loadStudentDashboard();
  }

  loadStudentDashboard() {
    const userId = this.authService.currentUserId();

    if (!userId) {
      this.error.set('User ID not found. Please log in again.');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    this.httpService.getStudentDashboard(userId).subscribe({
      next: (response: StudentDashboardResponse) => {
        // Set profile data
        this.studentName.set(response.student_name);
        this.studentId.set(response.student_id);
        this.rollNumber.set(response.roll_number);

        // Set attendance stats - with fallback calculations
        const attendanceHistory = response.attendance_history || [];
        const calculatedTotal = attendanceHistory.length;
        const calculatedPresent = attendanceHistory.filter(
          (r) => r.status === 'P'
        ).length;
        const calculatedAbsent = attendanceHistory.filter(
          (r) => r.status === 'A'
        ).length;

        // Use response values if available, otherwise use calculated
        this.totalClasses.set(response.total_classes ?? calculatedTotal);
        this.presentCount.set(response.present_count ?? calculatedPresent);
        this.absentCount.set(response.absent_count ?? calculatedAbsent);
        this.attendancePercentage.set(response.attendance_percentage);

        // Sort attendance history by date (newest first)
        const sorted = attendanceHistory.sort((a, b) => {
          // Parse date strings - handle both formats
          const dateA = this.parseDate(a.date);
          const dateB = this.parseDate(b.date);
          return dateB.getTime() - dateA.getTime();
        });
        this.attendanceHistory.set(sorted);

        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error response:', err);
        this.error.set(
          err.error?.message || 'Failed to load dashboard data. Please try again.'
        );
        console.error('Error loading dashboard:', err);
        this.loading.set(false);
      },
    });
  }

  // Helper function to parse date strings in various formats
  private parseDate(dateString: string): Date {
    // Handle "January 06, 2024" format
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const monthRegex = monthNames.join('|');
    const formattedDateRegex = new RegExp(
      `(${monthRegex})\\s+(\\d{1,2}),\\s+(\\d{4})`
    );

    const match = dateString.match(formattedDateRegex);
    if (match) {
      const [, month, day, year] = match;
      const monthIndex = monthNames.indexOf(month);
      return new Date(parseInt(year), monthIndex, parseInt(day));
    }

    // Fallback to standard date parsing
    return new Date(dateString);
  }

  refreshData() {
    this.loadStudentDashboard();
  }

  // Get recent records (last 10)
  getRecentRecords() {
    return this.attendanceHistory().slice(0, 10);
  }

  // Toggle sidebar
  toggleSidebar() {
    this.sidebarOpen.set(!this.sidebarOpen());
  }

  // Close sidebar
  closeSidebar() {
    this.sidebarOpen.set(false);
  }

  // Get attendance status color
  getStatusColor(percentage: number): string {
    if (percentage >= 85) return '#22c55e'; // Green
    if (percentage >= 70) return '#3b82f6'; // Blue
    if (percentage >= 50) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  }

  // Get status badge style
  getStatusBadgeClass(status: 'P' | 'A'): string {
    return status === 'P'
      ? 'status-badge status-present'
      : 'status-badge status-absent';
  }
}