# GPT Pilot UI Setup Guide

This guide covers setting up and using the GPT Pilot UI, a modern web interface for managing and interacting with GPT Pilot projects.

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# Start both frontend and backend services
docker-compose up
```

This will start:
- Frontend UI at http://localhost:3000
- Backend API at http://localhost:8000

## Manual Setup

### Backend Setup

1. Create and activate Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

4. Start the development server:
```bash
npm run dev
```

## Using the UI

### Creating a New Project

1. Click the "New Project" button
2. Fill in:
   - Project Name
   - Project Description
3. Click "Create"

### Starting Development with AI Agents

1. Click on a project name in the list
2. In the project detail page:
   - Enter your project requirements in the text area
   - Click "Start Development"
3. The AI agents will:
   - Analyze your requirements
   - Plan the development steps
   - Start implementing the code
   - Show progress in the development log

### Development Process

The UI integrates with GPT Pilot's AI agents:

1. **Product Owner**: Initial project setup
2. **Specification Writer**: Requirements clarification
3. **Architect**: Technology selection
4. **Tech Lead**: Development planning
5. **Developer**: Implementation planning
6. **Code Monkey**: Code implementation
7. **Reviewer**: Code review
8. **Troubleshooter**: Issue resolution
9. **Debugger**: Problem solving
10. **Technical Writer**: Documentation

### Monitoring Progress

The development log shows real-time updates from the AI agents, including:
- Current development stage
- Agent actions and decisions
- Code changes
- Error messages and solutions
- Development progress

## Troubleshooting

### Common Issues

1. Backend Connection Issues:
   ```
   "Not connected to GPT Pilot server"
   ```
   Solutions:
   - Check if backend is running
   - Verify CORS settings
   - Check API URL in `.env.local`

2. Project Creation Issues:
   ```
   "Failed to create project"
   ```
   Solutions:
   - Check backend logs
   - Verify database connection
   - Ensure all required fields are filled

3. Development Start Issues:
   ```
   "Failed to start development"
   ```
   Solutions:
   - Ensure project requirements are provided
   - Check API key configuration
   - Verify backend services are running

## Development Notes

### Key Files

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Projects list
│   │   └── project/[id]/page.tsx # Project detail
│   └── lib/
│       └── api/
│           └── client.ts         # API client
```

### API Endpoints

- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects/{id}/start` - Start development
- `POST /api/projects/{id}/pause` - Pause development

### Environment Variables

Frontend:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Additional Resources

- [Main GPT Pilot Documentation](./README.md)
- [Frontend Documentation](./frontend/README.md)
- [Join Discord Community](https://discord.gg/HaqXugmxr9)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here] 