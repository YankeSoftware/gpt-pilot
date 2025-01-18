'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, Project } from '@/lib/api/client';
import { MainLayout } from '@/components/layout/MainLayout';
import { socketService } from '@/lib/socket';

export default function ProjectDetail() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isStarting, setIsStarting] = useState(false);
  const [developmentLogs, setDevelopmentLogs] = useState<string[]>([]);

  useEffect(() => {
    // Connect to WebSocket when component mounts
    const socket = socketService.connect();
    socketService.joinProject(projectId);

    // Listen for development updates
    socketService.onDevelopmentUpdate((data) => {
      if (data.type === 'development_started') {
        setProject(prev => prev ? { ...prev, status: 'active' } : null);
      }
      setDevelopmentLogs(prev => [...prev, data.message]);
    });

    // Cleanup WebSocket connection when component unmounts
    return () => {
      socketService.disconnect();
    };
  }, [projectId]);

  useEffect(() => {
    async function loadProject() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProject(projectId);
        setProject(data);
      } catch (error) {
        console.error('Failed to load project:', error);
        setError('Failed to load project. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const handleStartDevelopment = async () => {
    if (!prompt.trim()) {
      setError('Please provide a description of what you want to build.');
      return;
    }

    try {
      setIsStarting(true);
      setError(null);
      await api.startDevelopment(projectId, prompt);
    } catch (error) {
      console.error('Failed to start development:', error);
      setError('Failed to start development. Please try again.');
      setIsStarting(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-gray-500">Loading project...</p>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-red-500">{error}</p>
        </div>
      </MainLayout>
    );
  }

  if (!project) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-gray-500">Project not found</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Project Header */}
        <div className="border-b border-gray-200 pb-5 sm:flex sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
              {project?.name}
            </h2>
            <p className="mt-1 text-sm text-gray-500">{project?.description}</p>
          </div>
          <div className="mt-3 sm:mt-0 sm:ml-4">
            <span className={`inline-flex items-center rounded-md px-2 py-1 text-sm font-medium ${
              project?.status === 'active' ? 'bg-green-100 text-green-700' :
              project?.status === 'error' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {project?.status}
            </span>
          </div>
        </div>

        {/* Development Section */}
        <div className="mt-8">
          <div className="space-y-4">
            <textarea
              rows={4}
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
              placeholder="Describe what you want to build..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isStarting || project?.status === 'active'}
            />
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleStartDevelopment}
              disabled={isStarting || project?.status === 'active' || !prompt.trim()}
            >
              {isStarting ? 'Starting Development...' : 'Start Development'}
            </button>
          </div>

          {/* Development Logs */}
          {developmentLogs.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900">Development Logs</h3>
              <div className="mt-2 bg-gray-50 rounded-md p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {developmentLogs.join('\n')}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
} 