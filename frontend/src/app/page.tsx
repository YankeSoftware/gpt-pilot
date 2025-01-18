'use client';

import { useEffect, useState } from 'react';
import { api, Project } from '@/lib/api/client';
import { MainLayout } from '@/components/layout/MainLayout';
import Link from 'next/link';

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [serverConnected, setServerConnected] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });

  useEffect(() => {
    async function checkServer() {
      const isConnected = await api.checkServer();
      setServerConnected(isConnected);
      return isConnected;
    }

    async function loadProjects() {
      try {
        setLoading(true);
        setError(null);
        
        const isConnected = await checkServer();
        if (!isConnected) {
          setError('Cannot connect to GPT Pilot server');
          return;
        }

        const data = await api.listProjects();
        setProjects(data);
      } catch (error) {
        console.error('Failed to load projects:', error);
        setError('Failed to load projects. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await api.createProject(newProject);
      setProjects([...projects, project]);
      setNewProject({ name: '', description: '' });
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to create project:', error);
      setError('Failed to create project. Please try again.');
    }
  };

  const openModal = () => {
    console.log('Opening modal');
    setIsModalOpen(true);
  };

  return (
    <MainLayout>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-semibold text-gray-900">Projects</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all your GPT Pilot projects
          </p>
          {!serverConnected && (
            <p className="mt-2 text-sm text-red-600">
              ⚠️ Not connected to GPT Pilot server
            </p>
          )}
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            disabled={!serverConnected}
            onClick={openModal}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
          >
            New Project
          </button>
        </div>
      </div>

      {/* New Project Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] overflow-y-auto bg-gray-500 bg-opacity-75">
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="relative w-full max-w-lg transform overflow-hidden rounded-lg bg-white p-6 text-left shadow-xl transition-all">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  onClick={() => setIsModalOpen(false)}
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div>
                <h3 className="text-lg font-semibold leading-6 text-gray-900">Create New Project</h3>
                <form onSubmit={handleCreateProject} className="mt-4">
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                        Project Name
                      </label>
                      <input
                        type="text"
                        id="name"
                        value={newProject.name}
                        onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                        Description
                      </label>
                      <textarea
                        id="description"
                        value={newProject.description}
                        onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                        rows={3}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        required
                      />
                    </div>
                  </div>
                  <div className="mt-5 flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => setIsModalOpen(false)}
                      className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      Create
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-8 flex flex-col">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle">
            <div className="overflow-hidden shadow-sm ring-1 ring-black ring-opacity-5">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6 lg:pl-8">
                      Name
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Description
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {loading ? (
                    <tr>
                      <td colSpan={4} className="px-3 py-4 text-sm text-gray-500 text-center">
                        Loading projects...
                      </td>
                    </tr>
                  ) : error ? (
                    <tr>
                      <td colSpan={4} className="px-3 py-4 text-sm text-red-500 text-center">
                        {error}
                      </td>
                    </tr>
                  ) : projects && projects.length > 0 ? (
                    projects.map((project) => (
                      <tr key={project.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 lg:pl-8">
                          <Link
                            href={`/projects/${project.id}`}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            {project?.name || 'Unnamed Project'}
                          </Link>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {project?.description || 'No description'}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                            project.status === 'active' ? 'bg-green-100 text-green-700' :
                            project.status === 'error' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {project?.status || 'Unknown'}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {project?.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-3 py-4 text-sm text-gray-500 text-center">
                        No projects found. Click "New Project" to create one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
