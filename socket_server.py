import logging
import socketio

logger = logging.getLogger(__name__)

class SocketServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            logger=True,
            engineio_logger=True,
            ping_timeout=5000,  # Reduced from 20000
            ping_interval=3000,  # Reduced from 25000
            max_http_buffer_size=1e8,
            allow_upgrades=True,
            http_compression=True
        )

        @self.sio.event
        async def connect(sid, environ):
            logger.debug(f"Client connected: {sid}")
            logger.debug(f"Transport: {environ.get('wsgi.url_scheme', 'unknown')}")
            logger.debug(f"Headers: {environ.get('headers', {})}")
            logger.debug(f"Query string: {environ.get('QUERY_STRING', '')}")
            logger.debug(f"Origin: {environ.get('HTTP_ORIGIN', 'unknown')}")
            logger.debug(f"Current transport: {self.sio.transport(sid)}")
            return True

        @self.sio.event
        async def disconnect(sid):
            logger.debug(f"Client disconnected: {sid}")

        @self.sio.event
        async def join_project(sid, project_id):
            logger.debug(f"Client {sid} joined project {project_id}")
            await self.sio.enter_room(sid, f"project_{project_id}")

    async def emit_development_update(self, project_id: str, update_type: str, message: str):
        await self.sio.emit(
            'development_update',
            {
                'type': update_type,
                'project_id': project_id,
                'message': message
            },
            room=f"project_{project_id}"
        )

    def get_asgi_app(self, other_asgi_app=None):
        return socketio.ASGIApp(
            self.sio,
            other_asgi_app,
            static_files={
                '/socket.io/': './node_modules/socket.io-client/dist/'
            }
        ) 