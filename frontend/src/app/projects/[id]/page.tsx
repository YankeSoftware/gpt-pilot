'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api, Project } from '@/lib/api/client';
import { MainLayout } from '@/components/layout/MainLayout';

export default function ProjectDetail() {
  const params = useParams();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isStarting, setIsStarting] = useState(false);

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

    loadProject();
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
      // Here we would typically start a WebSocket connection to receive real-time updates
      setProject(prev => prev ? { ...prev, status: 'active' } : null);
    } catch (error) {
      console.error('Failed to start development:', error);
      setError('Failed to start development. Please try again.');
    } finally {
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
              {project.name}
            </h2>
            <p className="mt-1 text-sm text-gray-500">{project.description}</p>
          </div>
          <div className="mt-3 sm:mt-0 sm:ml-4">
            <span className={`inline-flex items-center rounded-md px-2 py-1 text-sm font-medium ${
              project.status === 'active' ? 'bg-green-100 text-green-700' :
              project.status === 'error' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {project.status}
            </span>
          </div>
        </div>

        {/* Development Console */}
        <div className="mt-6 space-y-6">
          <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Development Console
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500">
                <p>Describe what you want to build and the AI agents will help you create it.</p>
              </div>
              <div className="mt-5">
                <textarea
                  rows={4}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="Describe your project requirements in detail..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>
              <div className="mt-5">
                <button
                  type="button"
                  onClick={handleStartDevelopment}
                  disabled={isStarting || project.status === 'active'}
                  className="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isStarting ? 'Starting Development...' : 'Start Development'}
                </button>
              </div>
            </div>
          </div>

          {/* Development Log */}
          <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Development Log
              </h3>
              <div className="mt-2">
                <div className="rounded-md bg-gray-50 px-6 py-5 font-mono text-sm text-gray-800 h-96 overflow-y-auto">
                  {/* This is where we'll show the development log from WebSocket updates */}
                  <p className="text-gray-500">Waiting to start development...</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 