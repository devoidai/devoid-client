import sys

from asyncio import AbstractEventLoop
from collections.abc import Coroutine

from .enums import *
from .messages import *
from .messages.components import *
from .gateway import GeneratorWebSocket
from .queue import QueueIsFullError, GenerationQueue

class GeneratorClient():
    def __init__(
            self,
            endpoint: str,
            service: str,
            token: str
        ) -> None:
        self.service = Service(service)
        self.gateway = GeneratorWebSocket(endpoint + f'/{service}', self.service, token)
        self.loop = None
        self.queue = GenerationQueue(self.gateway)
    
    def run(self, loop: AbstractEventLoop = None):
        self.loop = loop
        self.gateway.run(loop)
    
    async def text2img(
            self, 
            executor: Executor,
            premium: bool,
            moderate: bool,
            sync_with_s3: bool,
            user_id: str,
            chat_id: int,
            message_id: int,
            payload: dict,
            max_user_queue_size: int
        ) -> None:
        if not isinstance(executor, Executor):
            raise ValueError(f'Unknown type of executor "{executor}"')
        service_info = ServiceInfo(user_id=user_id, chat_id=chat_id, message_id=message_id)
        request = GenerationRequest(GenType.TEXT2IMG, executor, premium, moderate, sync_with_s3, service_info, payload)
        await self.queue.put(user_id, request, max_user_queue_size)
        
    async def img2img(
            self,
            executor: Executor,
            premium: bool,
            moderate: bool,
            sync_with_s3: bool,
            user_id: str,
            chat_id: int,
            message_id: int,
            payload: dict,
            max_user_queue_size: int
    ) -> None:
        if not isinstance(executor, Executor):
            raise ValueError(f'Unknown type of executor "{executor}"')
        if executor == Executor.KANDINSKY:
            raise ValueError(f'Executor {executor.value} cannot process img2img')
        service_info = ServiceInfo(user_id=user_id, chat_id=chat_id, message_id=message_id)
        request = GenerationRequest(GenType.IMG2IMG, executor, premium, moderate, sync_with_s3, service_info, payload)
        await self.queue.put(user_id, request, max_user_queue_size)

    async def mix2img(
            self,
            executor: Executor,
            premium: bool,
            moderate: bool,
            sync_with_s3: bool,
            user_id: str,
            chat_id: int,
            message_id: int,
            payload: dict,
            max_user_queue_size: int
    ) -> None:
        if not isinstance(executor, Executor):
            raise ValueError(f'Unknown type of executor "{executor}"')
        if executor != Executor.KANDINSKY:
            raise ValueError(f'Executor {executor.value} cannot process mix2img')
        service_info = ServiceInfo(user_id=user_id, chat_id=chat_id, message_id=message_id)
        request = GenerationRequest(GenType.MIX2IMG, executor, premium, moderate, sync_with_s3, service_info, payload)
        await self.queue.put(user_id, request, max_user_queue_size)

    def register_req_error_handler(self, handler: Coroutine):
        '''Register generator error handler\n
        `handler` - coroutine function with only `response: GenerationResponse` param
        '''
        self.gateway.req_error_handlers.append(handler)
        
    def register_req_queued_handler(self, handler: Coroutine):
        '''Register generator queued handler\n
        `handler` - coroutine function with only `response: GenerationResponse` param
        '''
        self.gateway.req_queued_handlers.append(handler)
    
    def register_req_generating_handler(self, handler: Coroutine):
        '''Register generator generating handler\n
        `handler` - coroutine function with only `response: GenerationResponse` param
        '''
        self.gateway.req_generating_handlers.append(handler)
    
    def register_req_done_handler(self, handler: Coroutine):
        '''Register generator generating handler\n
        `handler` - coroutine function with only `response: GenerationResponse` param
        '''
        self.gateway.req_done_handlers.append(handler)
        
    def register_con_error_handler(self, handler: Coroutine):
        '''Register generator generating handler\n
        `handler` - coroutine function with only `exception: Exception` param
        '''
        self.gateway.con_error_handlers.append(handler)