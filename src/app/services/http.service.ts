import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginRequest {
  id: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  role: 'student' | 'teacher';
  user_id?: string;
  user_name?: string;
  message: string;
  token?: string;
}

export interface Student {
  id: string;
  name: string;
  roll_number: string;
  status?: 'P' | 'A' | 'none';
}

export interface AttendancePayload {
  date: string;
  records: {
    student_id: string;
    status: 'P' | 'A';
  }[];
}

export interface StudentDashboardResponse {
  student_id: string;
  student_name: string;
  roll_number: string;
  total_classes: number;
  present_count: number;
  absent_count: number;
  attendance_percentage: number;
  attendance_history: {
    date: string;
    time: string;
    status: 'P' | 'A';
  }[];
}

export interface AttendanceRecord {
  id?: number;
  student: string;
  student_name?: string;
  student_roll?: string;
  course?: string;
  course_name?: string;
  date: string;
  status: 'P' | 'A';
  marked_at?: string;
  created_at?: string;
}

@Injectable({ providedIn: 'root' })
export class HttpService {
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

  // Login API
  login(id: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, {
      id,
      password
    });
  }

  // Set token after successful login
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('authToken', token);
  }

  // Clear token on logout
  clearToken() {
    this.token = null;
    localStorage.removeItem('authToken');
  }

  // Get all students for teacher
  getStudents(): Observable<Student[]> {
    return this.http.get<Student[]>(
      `${this.apiUrl}/students/`,
      { headers: this.getHeaders() }
    );
  }

  // Get attendance records for a given date
  getAttendanceByDate(date: string): Observable<AttendanceRecord[]> {
    return this.http.get<AttendanceRecord[]>(
      `${this.apiUrl}/attendance-by-date/${date}/`,
      { headers: this.getHeaders() }
    );
  }

  // Mark attendance - POST to backend
  markAttendance(attendanceData: AttendancePayload): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/mark-attendance/`,
      attendanceData,
      { headers: this.getHeaders() }
    );
  }

  // Get student dashboard data
  getStudentDashboard(studentId: string): Observable<StudentDashboardResponse> {
    return this.http.get<StudentDashboardResponse>(
      `${this.apiUrl}/student-dashboard/${studentId}/`,
      { headers: this.getHeaders() }
    );
  }

  // Get attendance report
  getAttendanceReport(courseId: string, date: string): Observable<any> {
    const params = {
      course: courseId,
      date: date
    };
    return this.http.get<any>(
      `${this.apiUrl}/attendance-report/`,
      { 
        headers: this.getHeaders(),
        params: params
      }
    );
  }

  // Upload marks
  uploadMarks(marksData: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/upload-marks/`,
      marksData,
      { headers: this.getHeaders() }
    );
  }

  // Get marks for a student
  getMarks(studentId: string): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/marks/${studentId}/`,
      { headers: this.getHeaders() }
    );
  }

  // Get all courses
  getCourses(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/courses/`,
      { headers: this.getHeaders() }
    );
  }
}