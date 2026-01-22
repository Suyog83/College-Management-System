import { inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { HttpService } from './http.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  userRole = signal<'student' | 'teacher' | null>(null);
  currentUser = signal<string | null>(null);
  currentUserId = signal<string | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);

  private router = inject(Router);
  private httpService = inject(HttpService);

  constructor() {
    this.restoreSession();
  }

  // Restore session from localStorage
  private restoreSession() {
    const storedRole = localStorage.getItem('userRole');
    const storedUser = localStorage.getItem('currentUser');
    const storedUserId = localStorage.getItem('currentUserId');

    if (storedRole && storedUser && storedUserId) {
      this.userRole.set(storedRole as 'student' | 'teacher');
      this.currentUser.set(storedUser);
      this.currentUserId.set(storedUserId);
    }
  }

  // Login with backend API
  login(id: string, password: string): Promise<boolean> {
    this.loading.set(true);
    this.error.set(null);

    return new Promise((resolve) => {
      this.httpService.login(id, password).subscribe({
        next: (response) => {
          if (response.success) {
            // Store token if provided
            if (response.token) {
              this.httpService.setToken(response.token);
            }

            // Set role and user info
            // Ensure user_id is always a string for consistency
            const userId = String(response.user_id || id);
            
            this.userRole.set(response.role);
            this.currentUser.set(response.user_name || id);
            this.currentUserId.set(userId);

            // Persist to localStorage
            localStorage.setItem('userRole', response.role);
            localStorage.setItem('currentUser', response.user_name || id);
            localStorage.setItem('currentUserId', userId);

            this.loading.set(false);
            resolve(true);
          } else {
            this.error.set(response.message || 'Login failed');
            this.loading.set(false);
            resolve(false);
          }
        },
        error: (err) => {
          // Better error handling
          let errorMessage = 'Network error. Please try again.';
          
          if (err.error?.message) {
            errorMessage = err.error.message;
          } else if (err.error?.error) {
            errorMessage = err.error.error;
          } else if (err.status === 401) {
            errorMessage = 'Invalid credentials. Please check your username and password.';
          } else if (err.status === 0) {
            errorMessage = 'Cannot connect to server. Is the backend running?';
          }
          
          this.error.set(errorMessage);
          this.loading.set(false);
          resolve(false);
        }
      });
    });
  }

  // Logout
  logout() {
    this.userRole.set(null);
    this.currentUser.set(null);
    this.currentUserId.set(null);
    this.error.set(null);
    
    // Clear storage
    localStorage.clear();
    this.httpService.clearToken();
    
    this.router.navigate(['/login']);
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.userRole() !== null;
  }

  // Get user ID as string (always consistent type)
  getCurrentUserIdAsString(): string {
    return this.currentUserId() || '';
  }
}