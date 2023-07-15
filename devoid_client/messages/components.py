import random

from typing import Dict, Union

from ..enums import *

class Result():
    content_type: ContentType
    content: str
    file_name: str
    
    def __init__(
            self, 
            content_type: ContentType, 
            content: str,
            file_name: str
        ) -> None:
        self.content_type = content_type
        self.content = content
        self.file_name = file_name
        
    @classmethod
    def from_dict(
            cls, 
            data: dict
        ):
        if data is None:
            data = {}
        content_type = data.get('content_type')
        content = data.get('content')
        file_name = data.get('file_name')
        return Result(content_type, content, file_name)
    
    def as_dict(self):
        return {
            "content_type": self.content_type.value,
            "content": self.content
        }

class Settings():
    premium: bool
    moderate: bool
    sync_with_s3: bool
    
    def __init__(
            self, 
            premium: bool = False, 
            moderate: bool = False,
            sync_with_s3: bool = False
        ) -> None:
        self.premium = premium
        self.moderate = moderate
        self.sync_with_s3 = sync_with_s3
    
    @classmethod
    def from_dict(
            cls, 
            data: dict
        ):
        if data is None:
            data = {}
        premium = data.get('premium')
        moderate = data.get('moderate')
        sync_with_s3 = data.get('sync_with_s3')
        return Settings(premium, moderate, sync_with_s3)

    def as_dict(self):
        return {
            "premium": self.premium,
            "moderate": self.moderate,
            "sync_with_s3": self.sync_with_s3
        }

class ServiceInfo():
    user_id: str

    def __init__(self, **kwargs) -> None:
        '''`user_id` is required field!'''
        if kwargs.get('user_id') is None:
            raise ValueError("Invalid args: user_id is required field")
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(
            cls, 
            data: Dict
        ) -> None:
        return ServiceInfo(**data)
        
    def as_dict(self) -> Dict:
        return self.__dict__

class ResponsePayload():
    prompt: str
    steps: int
    cfg_scale: int
    width: int
    height: int
    seed: int
    
    def __init__(
            self, 
            prompt: str,
            steps: int,
            cfg_scale: int,
            width: int,
            height: int,
            seed: int
        ) -> None:
        self.prompt = prompt
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.width = width
        self.height = height
        self.seed = seed
    
    @classmethod
    def from_dict(
            cls, 
            data: dict
        ):
        prompt = data.get('prompt')
        steps = data.get('steps')
        cfg_scale = data.get('cfg_scale')
        width = data.get('width')
        height = data.get('height')
        seed = data.get('seed')
        return ResponsePayload(prompt, steps, cfg_scale,\
            width, height, seed)
    
    def as_dict(self):
        return {
            "prompt": self.prompt,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "width": self.width,
            "height": self.height,
            "seed": self.seed
        }

class KandinskyPayload():
    images_texts: list  # MIX2IMG
    weights: list       # MIX2IMG
    prompt: str         # TEXT2IMG
    steps: int = 30,
    guidance_scale: int = 4, #(1 - Prompt игнорируется; 30 - Четко следовать запросу)
    height = 512,
    width = 512,
    sampler = 'p_sampler',
    prior_cf_scale = 4,
    prior_steps = '5',
    negative_prior_prompt = '',
    negative_decoder_prompt = ''

    def __init__(
            self,
            images_texts: list = None,  # MIX2IMG
            weights: list = None,       # MIX2IMG
            prompt: str = None,         # TEXT2IMG
            steps: int = None,
            guidance_scale: int = None, #(1 - Prompt игнорируется; 30 - Четко следовать запросу)
            height = None,
            width = None,
            sampler = None,
            prior_cf_scale = None,
            prior_steps = None,
            negative_prior_prompt = None,
            negative_decoder_prompt = None,
            no_check_defaults = False
        ) -> None:
        self.images_texts = images_texts    # MIX2IMG
        self.weights = weights              # MIX2IMG
        self.prompt = prompt                # TEXT2IMG
        self.steps = steps
        self.guidance_scale = guidance_scale
        self.height = height
        self.width = width
        self.sampler = sampler
        self.prior_cf_scale = prior_cf_scale
        self.prior_steps = prior_steps
        self.negative_prior_prompt = negative_prior_prompt
        self.negative_decoder_prompt = negative_decoder_prompt
        if no_check_defaults == False:
            self.check_default()

    @classmethod
    def from_dict(
            cls, 
            message: Dict,
            no_check_defaults = False
        ) -> None:
        if message is None:
            message = {}
        return KandinskyPayload(
            message.get("images_texts"), 
            message.get("weights"),
            message.get("prompt"), 
            message.get("steps"),
            message.get("guidance_scale"),
            message.get("height"),
            message.get("width"),
            message.get("sampler"),
            message.get("prior_cf_scale"),
            message.get("prior_steps"),
            message.get("negative_prior_prompt"),
            message.get("negative_decoder_prompt"),
            no_check_defaults = no_check_defaults
        )
    
    def check_default(self):
        if self.images_texts is None:
            self.images_texts = []
        if self.weights is None:
            self.weights = []
        if self.prompt is None:
            self.prompt = ''
        if self.steps is None:
            self.steps = 30
        if self.guidance_scale is None:
            self.guidance_scale = 4
        if self.height is None:
            self.height = 512
        if self.width is None:
            self.width = 512
        if self.sampler is None:
            self.sampler = 'p_sampler'
        if self.prior_cf_scale is None:
            self.prior_cf_scale = 4
        if self.prior_steps is None:
            self.prior_steps = '5'
        if self.negative_prior_prompt is None:
            self.negative_prior_prompt = ''
        if self.negative_decoder_prompt is None:
            self.negative_decoder_prompt = ''
    
    def as_dict(self):
        return self.__dict__

class Automatic1111Payload():
    prompt: str
    init_images: list
    steps: int
    cfg_scale: int
    sampler_index: str
    width: int
    height: int
    seed: int
    hr_scale: int
    hr_upscaler: str
    hr_second_pass_steps: int
    hr_resize_x: int
    hr_resize_y: int
    denoising_strength: float
    negative_prompt: str
    
    def __init__(
            self,
            prompt: str = None,
            init_images: list = None,
            steps: int = None,
            cfg_scale: int = None,
            sampler_index: str = None,
            width: int = None,
            height: int = None,
            seed: int = None,
            hr_scale: int = None,
            hr_upscaler: str = None,
            hr_second_pass_steps: int = None,
            hr_resize_x: int = None,
            hr_resize_y: int = None,
            denoising_strength: float = None,
            negative_prompt: str = None,
            no_check_defaults = False
        ) -> None:
        self.prompt = prompt
        self.init_images = init_images
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.sampler_index = sampler_index
        self.width = width
        self.height = height
        self.seed = seed
        self.hr_scale = hr_scale
        self.hr_upscaler = hr_upscaler
        self.hr_second_pass_steps = hr_second_pass_steps
        self.hr_resize_x = hr_resize_x
        self.hr_resize_y = hr_resize_y
        self.denoising_strength = denoising_strength
        self.negative_prompt = negative_prompt
        if no_check_defaults == False:
            self.check_default()
    
    @classmethod
    def from_dict(
            cls, 
            message: Dict,
            no_check_defaults = False
        ) -> None:
        if message is None:
            message = {}
        return Automatic1111Payload(
            message.get("prompt"), 
            message.get("init_images"),
            message.get("steps"), 
            message.get("cfg_scale"),
            message.get("sampler_index"),
            message.get("width"),
            message.get("height"),
            message.get("seed"),
            message.get("hr_scale"),
            message.get("hr_upscaler"),
            message.get("hr_second_pass_steps"),
            message.get("hr_resize_x"),
            message.get("hr_resize_y"),
            message.get("denoising_strength"),
            message.get("negative_prompt"),
            no_check_defaults=no_check_defaults
        )
    
    def check_default(self):
        if self.steps is None:
            self.steps = 30
        if self.cfg_scale is None:
            self.cfg_scale = 7
        if self.sampler_index is None:
            self.sampler_index = "Euler a"
        if self.width is None:
            self.width = 512
        if self.height is None:
            self.height = 768
        if self.seed is None:
            self.seed = random.randint(42, 4294967295)
        if self.hr_scale is None:
            self.hr_scale = 1
        if self.hr_upscaler is None:
            self.hr_upscaler = "Latent"
        if self.hr_second_pass_steps is None:
            self.hr_second_pass_steps = 0
        if self.hr_resize_x is None:
            self.hr_resize_x = 768
        if self.hr_resize_y is None:
            self.hr_resize_y = 1024
        if self.denoising_strength is None:
            self.denoising_strength = 0.7
        if self.negative_prompt is None:
            self.negative_prompt = "child, childish"
            
    def as_dict(self):
        return self.__dict__