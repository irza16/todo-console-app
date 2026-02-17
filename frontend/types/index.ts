/**
 * TypeScript interfaces for the Todo application.
 * These types mirror the backend Pydantic schemas.
 */

// User types
export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

// Authentication types
export interface SignupRequest {
  email: string;
  name: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Task types
export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority?: 'Low' | 'Medium' | 'High' | 'Urgent';
  tags?: string[] | string;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'weekdays' | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'Low' | 'Medium' | 'High' | 'Urgent';
  tags?: string[] | string;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'weekdays' | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: 'Low' | 'Medium' | 'High' | 'Urgent';
  tags?: string[] | string;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'weekdays' | null;
}

export interface TaskListResponse {
  tasks: Task[];
}

// API Error type
export interface ApiError {
  detail: string | Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}
