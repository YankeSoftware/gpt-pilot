import { io, Socket } from 'socket.io-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DevelopmentUpdate {
  type: string;
  project_id: string;
  message: string;
}

type DisconnectReason = 
  | 'io server disconnect' 
  | 'io client disconnect'
  | 'ping timeout'
  | 'transport close'
  | 'transport error';

class SocketService {
  private socket: Socket | null = null;
  private projectId: string | null = null;

  connect() {
    if (!this.socket) {
      console.log('Connecting to Socket.IO server at:', API_URL);
      
      this.socket = io(API_URL, {
        transports: ['polling'],
        autoConnect: true,
        withCredentials: true,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        timeout: 5000,
        forceNew: true,
        path: '/socket.io/'
      });

      this.socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
        console.log('Transport:', this.socket?.io.engine.transport.name);
        console.log('Socket ID:', this.socket?.id);
        
        this.socket?.io?.engine?.once('upgrade', () => {
          console.log('Transport upgraded to websocket');
        });
        
        if (this.projectId) {
          this.joinProject(this.projectId);
        }
      });

      this.socket.on('disconnect', (reason: DisconnectReason) => {
        console.log('Disconnected from Socket.IO server:', reason);
        if (reason === 'io server disconnect' || reason === 'transport close') {
          setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.socket?.connect();
          }, 1000);
        }
      });

      this.socket.on('connect_error', (error: Error) => {
        console.error('Socket.IO connection error:', error);
        if (this.socket?.io?.engine?.transport?.name === 'websocket') {
          console.log('Falling back to polling transport');
          this.socket.io.opts.transports = ['polling'];
        }
      });

      this.socket.on('error', (error: Error) => {
        console.error('Socket.IO error:', error);
      });
    }
    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.projectId = null;
    }
  }

  joinProject(projectId: string) {
    if (this.socket?.connected) {
      this.projectId = projectId;
      this.socket.emit('join_project', projectId);
    } else {
      this.projectId = projectId;
      this.connect();
    }
  }

  onDevelopmentUpdate(callback: (data: DevelopmentUpdate) => void) {
    if (this.socket) {
      this.socket.on('development_update', callback);
    }
  }

  offDevelopmentUpdate(callback: (data: DevelopmentUpdate) => void) {
    if (this.socket) {
      this.socket.off('development_update', callback);
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const socketService = new SocketService(); 