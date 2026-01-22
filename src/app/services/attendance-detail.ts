import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AttendanceDetail {
  student_id: string;
  student_name: string;
  roll_number: string;
  total_classes: number;
  present_count: number;
  absent_count: number;
  overall_percentage: number;
  attendance_by_month: MonthlyAttendance[];
}

export interface MonthlyAttendance {
  month: string;
  total: number;
  present: number;
  absent: number;
  percentage: number;
  records: AttendanceRecord[];
}

export interface AttendanceRecord {
  date: string;
  status: 'P' | 'A';
  time: string;
}

export interface AttendanceStatistics {
  student_id: string;
  student_name: string;
  overall_attendance: {
    total: number;
    present: number;
    absent: number;
    percentage: number;
  };
  current_streak: number;
  last_7_days: {
    total: number;
    present: number;
    percentage: number;
  };
  last_30_days: {
    total: number;
    present: number;
    percentage: number;
  };
}

export interface TeacherAttendanceSummary {
  total_students: number;
  students: StudentAttendanceSummary[];
}

export interface StudentAttendanceSummary {
  student_id: string;
  student_name: string;
  roll_number: string;
  total_classes: number;
  present: number;
  absent: number;
  percentage: number;
}

export interface DateRangeAttendance {
  student_id: string;
  student_name: string;
  date_range: string;
  total: number;
  present: number;
  absent: number;
  percentage: number;
  records: AttendanceRecord[];
}

@Injectable({ providedIn: 'root' })
export class AttendanceDetailService {
  private apiUrl = 'http://127.0.0.1:8000/api';
  private token: string | null = null;

  constructor(private http: HttpClient) {
    this.loadToken();
  }

  private loadToken() {
    this.token = localStorage.getItem('authToken');
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    if (this.token) {
      headers = headers.set('Authorization', `Bearer ${this.token}`);
    }
    return headers;
  }

  // Get detailed attendance information for a student
  getAttendanceDetail(studentId: string): Observable<AttendanceDetail> {
    return this.http.get<AttendanceDetail>(
      `${this.apiUrl}/attendance-detail/${studentId}/`,
      { headers: this.getHeaders() }
    );
  }

  // Get attendance statistics and trends
  getAttendanceStatistics(studentId: string): Observable<AttendanceStatistics> {
    return this.http.get<AttendanceStatistics>(
      `${this.apiUrl}/attendance-statistics/${studentId}/`,
      { headers: this.getHeaders() }
    );
  }

  // Get teacher attendance summary (all students)
  getTeacherAttendanceSummary(): Observable<TeacherAttendanceSummary> {
    return this.http.get<TeacherAttendanceSummary>(
      `${this.apiUrl}/teacher-attendance-summary/`,
      { headers: this.getHeaders() }
    );
  }

  // Get attendance for a date range
  getAttendanceByDateRange(
    studentId: string,
    startDate: string,
    endDate: string
  ): Observable<DateRangeAttendance> {
    const params = {
      start_date: startDate,
      end_date: endDate
    };
    return this.http.get<DateRangeAttendance>(
      `${this.apiUrl}/attendance-by-date-range/${studentId}/`,
      {
        headers: this.getHeaders(),
        params: params
      }
    );
  }
}