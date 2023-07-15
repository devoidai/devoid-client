import logging

from asyncio.locks import Lock
from .gateway import GeneratorWebSocket
from queue import Queue
from typing import Dict
from .messages import GenerationRequest, GenerationResponse

class QueueIsFullError(Exception):
    pass

class UserRequestBuffer:
    id: str
    max_size: int
    cur_size: int
    queue: Queue
    
    lock: Lock
    generating: bool
    gateway: GeneratorWebSocket

    def __init__(
            self, 
            id: str, 
            max_size: int,
            gateway: GeneratorWebSocket
        ) -> None:
        self.id = id
        self.cur_size = 0
        self.max_size = max_size
        self.queue = Queue()
        self.lock = Lock()
        self.generating = False
        self.gateway = gateway
        
    async def add_request(
            self, 
            request: GenerationRequest
        ) -> None:
        async with self.lock:
            if self.cur_size >= self.max_size:
                raise QueueIsFullError("Cannot add new request, because user's queue is full")
            logging.debug(f'Adding new request of user `{self.id}`')
            self.queue.put_nowait(request)
            self.cur_size += 1
            if self.generating == False:
                logging.debug(f'Starting generating for user `{self.id}`')
                request = self.queue.get_nowait()
                self.generating = True
                await self.gateway.send_message(request.as_dict())
            return True
    
    async def on_response(self, response: GenerationResponse):
        async with self.lock:
            self.cur_size -= 1
            if self.cur_size < 1:
                self.generating = False
                logging.debug(f'ReqBuffer for user `{self.id}` is empty, not sending request')
                return
            request: GenerationRequest = self.queue.get_nowait()
            logging.debug(f'Sending another request for user `{self.id}`')
            await self.gateway.send_message(request.as_dict())
        
    async def get_size(self, request) -> bool:
        async with self.lock:
            return self.cur_size
    
class GenerationQueue:
    users_bufs: Dict[str, UserRequestBuffer]
    gateway: GeneratorWebSocket

    def __init__(
            self,
            gateway: GeneratorWebSocket
        ) -> None:
        self.users_bufs = dict()
        self.gateway = gateway
        self.gateway.req_done_handlers.append(self.req_done_handler)
        self.gateway.req_error_handlers.append(self.req_error_handler)
        self.gateway.con_error_handlers.append(self.con_error_handler)
    
    async def put(
            self, 
            user_id: str, 
            request: GenerationRequest,
            max_user_queue_size: int
        ) -> bool:
        user_buf = self.users_bufs.get(user_id)
        if user_buf is None:
            user_buf = UserRequestBuffer(user_id, max_user_queue_size, self.gateway)
            self.users_bufs[user_id] = user_buf
        user_buf.max_size = max_user_queue_size
        await user_buf.add_request(request)
        
    async def remove(
        self
    ) -> bool:
        raise NotImplementedError('`remove` method not implemented')
    
    async def req_error_handler(self, response: GenerationResponse):
        user_id = response.service_info.user_id
        user_buf = self.users_bufs.get(user_id)
        if user_buf is None:
            return
        await user_buf.on_response(response)
    
    async def req_done_handler(self, response: GenerationResponse):
        user_id = response.service_info.user_id
        user_buf = self.users_bufs.get(user_id)
        if user_buf is None:
            return
        await user_buf.on_response(response)
        
    async def con_error_handler(self, response: GenerationResponse):
        logging.warning('Got WebsocketConnectionError all buffers has been cleaned!')
        self.users_bufs = dict()
    
