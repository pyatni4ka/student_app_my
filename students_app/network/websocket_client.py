import asyncio
import json
import websockets
import logging
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class TestingClient:
    def __init__(self, student_id: str, host: str = 'localhost', port: int = 8765):
        self.student_id = student_id
        self.host = host
        self.port = port
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.heartbeat_task = None
        self.reconnect_task = None
        self.on_test_received: Optional[Callable] = None
        
    async def connect(self):
        while True:
            try:
                uri = f"ws://{self.host}:{self.port}"
                self.websocket = await websockets.connect(uri)
                
                # Регистрация на сервере
                await self.websocket.send(json.dumps({
                    'type': 'register',
                    'student_id': self.student_id
                }))
                
                self.connected = True
                logger.info(f"Подключено к серверу {uri}")
                
                # Запускаем heartbeat
                if self.heartbeat_task is None:
                    self.heartbeat_task = asyncio.create_task(self.heartbeat())
                
                return True
            except Exception as e:
                logger.error(f"Ошибка подключения: {e}")
                await asyncio.sleep(5)  # Пауза перед повторной попыткой
                
    async def heartbeat(self):
        while self.connected:
            try:
                await self.websocket.send(json.dumps({'type': 'heartbeat'}))
                await asyncio.sleep(30)  # Пинг каждые 30 секунд
            except:
                self.connected = False
                if self.reconnect_task is None:
                    self.reconnect_task = asyncio.create_task(self.reconnect())
                break
                
    async def reconnect(self):
        logger.info("Попытка переподключения...")
        await self.connect()
        self.reconnect_task = None
        
    async def send_test_result(self, result_data: dict):
        if self.connected:
            try:
                await self.websocket.send(json.dumps({
                    'type': 'test_result',
                    'data': result_data
                }))
            except Exception as e:
                logger.error(f"Ошибка отправки результатов: {e}")
                self.connected = False
                if self.reconnect_task is None:
                    self.reconnect_task = asyncio.create_task(self.reconnect())
                    
    async def receive_messages(self):
        while True:
            try:
                if not self.connected:
                    await asyncio.sleep(1)
                    continue
                    
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data['type'] == 'test_data' and self.on_test_received:
                    await self.on_test_received(data['data'])
                elif data['type'] == 'heartbeat_response':
                    continue
                    
            except Exception as e:
                logger.error(f"Ошибка получения сообщения: {e}")
                self.connected = False
                if self.reconnect_task is None:
                    self.reconnect_task = asyncio.create_task(self.reconnect())
                await asyncio.sleep(1)
                
    async def close(self):
        self.connected = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.reconnect_task:
            self.reconnect_task.cancel()
        if self.websocket:
            await self.websocket.close()
