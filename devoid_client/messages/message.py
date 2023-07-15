from typing import Dict, Union

from .components import *
from ..enums import *

class GenerationRequest():
    message_type: MessageType
    executor: Executor
    gen_type: GenType
    
    settings: Settings
    service_info: ServiceInfo
    payload: Union[Automatic1111Payload, KandinskyPayload]
    
    def __init__(
            self,
            gen_type: GenType,
            executor: Executor,
            premium: bool,
            moderate: bool,
            sync_with_s3: bool,
            service_info: ServiceInfo,
            payload: dict
        ) -> None:
        self.message_type = MessageType.REQUEST
        self.executor = executor
        self.gen_type = gen_type
        self.settings = Settings(premium, moderate, sync_with_s3)
        self.service_info = service_info
        if self.executor == Executor.AUTOMATIC1111:
            self.payload = Automatic1111Payload.from_dict(payload)
        elif self.executor == Executor.KANDINSKY:
            self.payload = KandinskyPayload.from_dict(payload)
    
    def as_dict(self):
        return {
            "message_type": self.message_type.value,
            "executor": self.executor.value,
            "gen_type": self.gen_type.value,
            "settings": self.settings.as_dict(),
            "service_info": self.service_info.as_dict(),
            "payload": self.payload.as_dict()
        }

class GenerationResponse():
    object_id: str
    message_type: str
    executor: Executor

    gen_type: GenType
    gen_status: GenStatus
    
    avg_time: float
    
    result: Union[Result, None]
    settings: Union[Settings, None]
    service_info: ServiceInfo
    payload: Union[Automatic1111Payload, KandinskyPayload, None]
    
    def __init__(self, data: dict):
        self.object_id = data.get('object_id')
        self.message_type = data.get('message_type')
        self.executor = Executor(data.get('executor'))
        self.gen_type = GenType(data.get('gen_type'))
        self.gen_status = GenStatus(data.get('gen_status'))
        self.avg_time = data.get('avg_time')
        
        self.result = None
        self.settings = None
        self.service_info = None
        self.payload = None
        
        # result
        data_ = data.get('result')
        if not data_ is None:
            self.result = Result.from_dict(data_)
        # settings
        data_ = data.get('settings')
        if not data_ is None:
            self.settings = Settings.from_dict(data_)
        # service info
        data_ = data.get('service_info')
        if not data_ is None:
            self.service_info = ServiceInfo.from_dict(data_)
        # payload
        data_ = data.get('payload')
        if not data_ is None:
            if self.executor == Executor.AUTOMATIC1111:
                self.payload = Automatic1111Payload.from_dict(data_, True)
            elif self.executor == Executor.KANDINSKY:
                self.payload = KandinskyPayload.from_dict(data_, True)
        
    def __str__(self) -> str:
        return f"GenerationResponse({self.object_id}: {self.gen_type.value})"