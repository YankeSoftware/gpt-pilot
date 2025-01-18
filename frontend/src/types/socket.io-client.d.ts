declare module 'socket.io-client' {
    import { Socket as BaseSocket, SocketOptions } from '@types/socket.io-client';
    export { SocketOptions };
    export type Socket = BaseSocket;
    export function io(uri: string, opts?: Partial<SocketOptions>): Socket;
} 