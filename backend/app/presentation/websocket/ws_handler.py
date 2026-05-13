"""
WebSocket Handler — Real-Time Communication
==============================================
Kullaniciya anlik geri bildirim ve sistem guncellemelerini
iletmek amaciyla WebSocket altyapisi.

flask-socketio ile Socket.IO protokolu kullanilir.
"""

import logging

logger = logging.getLogger(__name__)

# flask-socketio opsiyonel
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    SocketIO = None

socketio_instance = None


def init_websocket(app):
    """Flask uygulamasina WebSocket destegi ekle."""
    global socketio_instance

    if not HAS_SOCKETIO:
        logger.warning(
            "[WebSocket] flask-socketio yuklu degil. "
            "Real-time ozellikler devre disi."
        )
        return None

    socketio_instance = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    @socketio_instance.on("connect")
    def handle_connect():
        logger.info("[WebSocket] Client baglandi")
        emit("server_message", {"message": "Baglanti basarili"})

    @socketio_instance.on("disconnect")
    def handle_disconnect():
        logger.info("[WebSocket] Client ayrildi")

    @socketio_instance.on("join_room")
    def handle_join(data):
        room = data.get("room", "general")
        join_room(room)
        logger.info(f"[WebSocket] Client odaya katildi: {room}")
        emit("server_message", {"message": f"Oda '{room}' katildi"}, room=room)

    @socketio_instance.on("leave_room")
    def handle_leave(data):
        room = data.get("room", "general")
        leave_room(room)
        logger.info(f"[WebSocket] Client odadan ayrildi: {room}")

    logger.info("[WebSocket] Real-time communication baslatildi")
    return socketio_instance


def broadcast_event(event_type: str, data: dict, room: str = None):
    """Tum bagli client'lara veya belirli odaya event yayinla."""
    if socketio_instance is None:
        return

    try:
        if room:
            socketio_instance.emit(event_type, data, room=room)
        else:
            socketio_instance.emit(event_type, data, broadcast=True)
        logger.info(f"[WebSocket] Broadcast: {event_type}")
    except Exception as e:
        logger.error(f"[WebSocket] Broadcast hatasi: {e}")
