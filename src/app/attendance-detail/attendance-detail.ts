import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AttendanceDetailService, AttendanceDetail, MonthlyAttendance } from '../services/attendance-detail';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-attendance-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './attendance-detail.html',
  styleUrl: './attendance-detail.css'
})
export class AttendanceDetailComponent implements OnInit {
  private attendanceService = inject(AttendanceDetailService);
  private authService = inject(AuthService);
  private router = inject(Router);

  //wrapper for the logout action
  logout(){
    this.authService.logout();
  }
  //getter for the user information
  get currentUser(){
    return
    this.authService.currentUser();
  }

  // Data signals
  attendanceDetail = signal<AttendanceDetail | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  expandedMonth = signal<string | null>(null);

  // Date range filter
  startDate = signal('');
  endDate = signal('');
  filterApplied = signal(false);

  ngOnInit() {
    const userId = this.authService.currentUserId();
    if (userId) {
      this.loadAttendanceDetail(userId);
    } else {
      this.error.set('User not authenticated');
    }
  }

  loadAttendanceDetail(studentId: string) {
    this.loading.set(true);
    this.error.set(null);

    this.attendanceService.getAttendanceDetail(studentId).subscribe({
      next: (data) => {
        this.attendanceDetail.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load attendance details');
        console.error('Error:', err);
        this.loading.set(false);
      }
    });
  }

  toggleMonth(month: string) {
    if (this.expandedMonth() === month) {
      this.expandedMonth.set(null);
    } else {
      this.expandedMonth.set(month);
    }
  }

  getStatusColor(status: 'P' | 'A'): string {
    return status === 'P' ? '#10b981' : '#ef4444';
  }

  getStatusLabel(status: 'P' | 'A'): string {
    return status === 'P' ? 'Present' : 'Absent';
  }

  goBack() {
    this.router.navigate(['/student']);
  }

  getAttendanceColor(percentage: number): string {
    if (percentage >= 85) return '#10b981';
    if (percentage >= 70) return '#3b82f6';
    if (percentage >= 50) return '#f59e0b';
    return '#ef4444';
  }
}