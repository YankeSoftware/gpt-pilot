import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'error';
  created_at: string;
}

export const api = {
  // Project endpoints
  async listProjects(): Promise<Project[]> {
    try {
      const response = await apiClient.get('/api/projects');
      return response.data?.projects ?? [];
    } catch (error) {
      console.error('Error fetching projects:', error);
      return [];
    }
  },

  async getProject(id: string): Promise<Project> {
    const response = await apiClient.get(`/api/projects/${id}`);
    return response.data;
  },

  async createProject(data: { name: string; description: string }): Promise<Project> {
    const response = await apiClient.post('/api/projects', data);
    return response.data;
  },

  // Development endpoints
  async startDevelopment(projectId: string, requirements: string): Promise<void> {
    await apiClient.post(`/api/projects/${projectId}/start`, {
      requirements,
    });
  },

  async pauseDevelopment(projectId: string): Promise<void> {
    await apiClient.post(`/api/projects/${projectId}/pause`);
  },

  // Utility endpoints
  async checkServer(): Promise<boolean> {
    try {
      await apiClient.get('/');
      return true;
    } catch (error) {
      return false;
    }
  }
}; 