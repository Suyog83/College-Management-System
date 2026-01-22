import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  // Use regular properties for two-way binding with [(ngModel)]
  email = '';
  password = '';
  role = 'Student';
  
  // Use signals for state management
  loading = signal(false);
  error = signal<string | null>(null);

  private router = inject(Router);
  private auth = inject(AuthService);

  async onLogin() {
    if (!this.email || !this.password) {
      this.error.set('Please fill in all fields');
      return;
    }

    this.error.set(null);
    this.loading.set(true);

    // Map Student role to student login format
    let loginId = this.email;
    let loginPassword = this.password;

    // Handle different role formats
    if (this.role === 'Student') {
      // If user enters email, keep as is (e.g., "Arjun-101")
      if (!this.email.includes('@')) {
        loginId = this.email;
      }
    } else if (this.role === 'Teacher') {
      loginId = this.email || 'admin';
    }

    const success = await this.auth.login(loginId, loginPassword);

    if (success) {
      const userRole = this.auth.userRole();
      if (userRole === 'teacher') {
        this.router.navigate(['/teacher']);
      } else if (userRole === 'student') {
        this.router.navigate(['/student']);
      }
    } else {
      this.error.set(this.auth.error() || 'Login failed. Please try again.');
      this.loading.set(false);
    }
  }

  // Quick login helpers
  quickLoginStudent() {
    this.email = 'Arjun-101';
    this.password = 'student123';
    this.role = 'Student';
  }

  quickLoginTeacher() {
    this.email = 'admin';
    this.password = 'teacher123';
    this.role = 'Teacher';
  }
}