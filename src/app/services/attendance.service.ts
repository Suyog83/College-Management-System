import { Injectable, signal } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AttendanceRecord {
  studentId: string;
  studentName: string;
  status: 'P' | 'A' | 'none';
  date: string;
  time: string;
}

export interface StudentAttendanceHistory {
  studentId: string;
  records: AttendanceRecord[];
}

@Injectable({ providedIn: 'root' })
export class AttendanceService {
  // Store all attendance records
  private attendanceData = signal<AttendanceRecord[]>([]);
  
  // Observable for real-time updates
  private attendanceSubject = new BehaviorSubject<AttendanceRecord[]>([]);
  attendanceUpdates$ = this.attendanceSubject.asObservable();

  constructor() {
    this.loadAttendanceData();
  }

  // Load attendance from localStorage or initialize empty
  private loadAttendanceData() {
    const stored = localStorage.getItem('attendanceRecords');
    if (stored) {
      const records = JSON.parse(stored);
      this.attendanceData.set(records);
      this.attendanceSubject.next(records);
    }
  }

  // Save attendance record (called by teacher)
  saveAttendanceRecord(studentId: string, studentName: string, status: 'P' | 'A') {
    const now = new Date();
    const date = now.toLocaleDateString('en-IN', { 
      year: 'numeric', 
      month: 'long', 
      day: '2-digit' 
    });
    const time = now.toLocaleTimeString('en-IN');

    const newRecord: AttendanceRecord = {
      studentId,
      studentName,
      status,
      date,
      time
    };

    const allRecords = [...this.attendanceData(), newRecord];
    this.attendanceData.set(allRecords);
    
    // Persist to localStorage
    localStorage.setItem('attendanceRecords', JSON.stringify(allRecords));
    
    // Broadcast the update
    this.attendanceSubject.next(allRecords);
  }

  // Get attendance history for a specific student
  getStudentHistory(studentId: string): AttendanceRecord[] {
    return this.attendanceData().filter(record => record.studentId === studentId);
  }

  // Get today's attendance for a student
  getTodayAttendance(studentId: string): AttendanceRecord | undefined {
    const today = new Date().toLocaleDateString('en-IN', { 
      year: 'numeric', 
      month: 'long', 
      day: '2-digit' 
    });
    return this.attendanceData().find(
      record => record.studentId === studentId && record.date === today
    );
  }

  // Get all attendance records (for teacher)
  getAllRecords(): AttendanceRecord[] {
    return this.attendanceData();
  }

  // Calculate attendance percentage for a student
  calculateAttendancePercentage(studentId: string): number {
    const records = this.getStudentHistory(studentId);
    if (records.length === 0) return 0;
    const presentDays = records.filter(r => r.status === 'P').length;
    return Math.round((presentDays / records.length) * 100);
  }

  // Bulk save attendance (called after teacher submits)
  bulkSaveAttendance(records: { studentId: string; studentName: string; status: 'P' | 'A' | 'none' }[]) {
    records.forEach(record => {
      if (record.status === 'P' || record.status === 'A') {
        this.saveAttendanceRecord(record.studentId, record.studentName, record.status);
      }
    });
  }
}