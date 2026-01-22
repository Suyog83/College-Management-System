import { Routes, Router, CanActivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../app/services/auth.service';
import { Login } from './login/login';
import { StudentDashboard } from './student-dashboard/student-dashboard';
import { TeacherDashboard } from './teacher-dashboard/teacher-dashboard';
import { AttendanceDetailComponent } from '../app/attendance-detail/attendance-detail';

// Student route guard
const studentGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.userRole() === 'student') {
    return true;
  }
  return router.createUrlTree(['/login']);
};

// Teacher route guard
const teacherGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.userRole() === 'teacher') {
    return true;
  }
  return router.createUrlTree(['/login']);
};

export const routes: Routes = [
  { path: 'login', component: Login },
  { 
    path: 'student', 
    component: StudentDashboard,
    canActivate: [studentGuard]
  },
  { 
    path: 'dashboard',
    component: StudentDashboard,
    canActivate: [studentGuard]
  },
  { 
    path: 'attendance-detail', 
    component: AttendanceDetailComponent,
    canActivate: [studentGuard]
  },
  { 
    path: 'teacher', 
    component: TeacherDashboard,
    canActivate: [teacherGuard]
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];