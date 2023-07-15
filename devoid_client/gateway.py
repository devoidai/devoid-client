import json
import logging
import asyncio

from typing import List
from websockets.client import connect
from websockets.exceptions import *

from .messages import *
from .enums import *

class GeneratorWebSocket():    
    req_done_handlers: List
    req_error_handlers: List
    req_queued_handlers: List
    req_generating_handlers: List
    
    def __init__(
            self, 
            endpoint: str,
            service: Service,
            token: str
        ) -> None:
        self.endpoint = endpoint
        self.service = service
        self.token = token
        self.websocket = None
        self.connected = False
        
        self.req_done_handlers = []
        self.req_error_handlers = []
        self.req_queued_handlers = []
        self.req_generating_handlers = []
        
        self.con_error_handlers = []
    
    def run(self, loop = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        loop.create_task(self.receiver_loop())
    
    async def send_message(self, message: dict):
        await self.websocket.send(json.dumps(message))
            
    async def connect(self):
        while not self.connected:
            try:
                self.websocket = await connect(self.endpoint, extra_headers=\
                            {'authorization': self.token, 'service': self.service.value})
                self.connected = True
            except ConnectionRefusedError as e:
                logging.error(e)
                await asyncio.sleep(5)
            except InvalidStatusCode as e:
                logging.error('Service or token is not valid')
                exit()
            except Exception as e:
                logging.error(type(e))
                await asyncio.sleep(5)
        return
    
    async def receiver_loop(self):
        while True:
            await self.connect()
            logging.info('Connection established!')
            try:
                async for raw_message in self.websocket:
                    json_message = json.loads(raw_message)
                    message_type = MessageType(json_message.get('message_type'))
                    if message_type == MessageType.RESPONSE:
                        loop = asyncio.get_running_loop()
                        response = GenerationResponse(json_message)
                        if response.gen_status == GenStatus.OK:
                            for handler in self.req_done_handlers:
                                loop.create_task(handler(response))
                        elif response.gen_status == GenStatus.ERROR:
                            for handler in self.req_error_handlers:
                                loop.create_task(handler(response))
                        elif response.gen_status == GenStatus.QUEUED:
                            for handler in self.req_queued_handlers:
                                loop.create_task(handler(response))
                        elif response.gen_status == GenStatus.GENERATING:
                            for handler in self.req_generating_handlers:
                                loop.create_task(handler(response))
            except Exception as e:
                logging.error(f'[{type(e)}] {e}')
                for handler in self.con_error_handlers:
                    await handler(e)
            finally:
                self.connected = False
            logging.warning('Connection lost, trying to reconnect')
            await asyncio.sleep(2)