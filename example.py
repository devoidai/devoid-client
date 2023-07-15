import os
import base64
import asyncio
import requests

from datetime import datetime
from devoid_client import GeneratorClient, GenerationResponse, QueueIsFullError
from devoid_client.enums import Executor

from random import randint

GENERATOR_ENDPOINT = 'ws://localhost:8080/ws'
SERVICE_NAME = 'discord'
SERVICE_TOKEN = 'service-token'

expecting = {}

if not os.path.exists("gens/"):
    os.makedirs("gens/")

# Connection lost handler
async def connection_error_handler(exception: Exception):
    print(f'[{type(exception)}] {exception}')

# Done handler
async def request_done_handler(response: GenerationResponse):
    msg = '\n'
    msg +=  '| REQUEST DONE\n'
    msg += f'| GenerationID: {response.object_id}\n'
    msg += f'| Executor: {response.executor.value}\n'
    msg += f'| GenerationType: {response.gen_status.name}|{response.gen_type.name}\n'
    msg += f'| GenerationUser: {response.service_info.user_id}\n'
    msg += f'| GenerationResult: {response.result.content}\n'    
    msg += f'| FILE_NAME: {response.result.file_name}\n'    
    print(msg)
    try:
        r = requests.get(response.result.content, timeout=3)
        with open(f'gens/{response.result.content.split("/")[-1]}', 'wb') as f:
            f.write(r.content)
            
        with open('stats.txt', 'a') as f:
            f.write(f'{str(response.settings.premium)}\n')
        
        expecting[response.object_id].append(datetime.now())
        td = expecting[response.object_id][2] - expecting[response.object_id][1]
        td = round(td.total_seconds(), 2)
        ed = expecting[response.object_id][0]
        with open('expecting.txt', 'a') as f:
            f.write(f'{response.object_id} {ed} - {td} = {ed - td}\n')
    except Exception as e:
        print(e)

async def request_error_handler(response: GenerationResponse):
    msg = '\n'
    msg +=  '| REQUEST FAILED\n'
    msg += f'| GenerationID: {response.object_id}\n'
    msg += f'| Executor: {response.executor.value}\n'
    msg += f'| GenerationType: {response.gen_status.name}|{response.gen_type.name}\n'
    msg += f'| GenerationUser: {response.service_info.user_id}\n'
    msg += f'| GenerationError: {response.result.content}\n'
    print(msg)

async def request_queued_handler(response: GenerationResponse):
    msg = '\n'
    msg +=  '| REQUEST QUEUED\n'
    msg += f'| GenerationID: {response.object_id}\n'
    msg += f'| Executor: {response.executor.value}\n'
    msg += f'| GenerationType: {response.gen_status.name}|{response.gen_type.name}\n'
    msg += f'| GenerationUser: {response.service_info.user_id}\n'
    msg += f'| GenerationAvgTime: {response.avg_time}\n'
    expecting[response.object_id] = [response.avg_time, datetime.now()]
    print(msg)
    
async def request_generating_handler(response: GenerationResponse):
    msg = '\n'
    msg +=  '| REQUEST GENERATING\n'
    msg += f'| GenerationID: {response.object_id}\n'
    msg += f'| Executor: {response.executor.value}\n'
    msg += f'| GenerationType: {response.gen_status.name}|{response.gen_type.name}\n'
    msg += f'| GenerationUser: {response.service_info.user_id}\n'
    print(msg)

async def main():
    # Creating client
    client1 = GeneratorClient(
        endpoint=GENERATOR_ENDPOINT,
        service=SERVICE_NAME,
        token=SERVICE_TOKEN
    )

    # Registering handlers
    client1.register_req_done_handler(request_done_handler)
    client1.register_req_error_handler(request_error_handler)
    client1.register_req_generating_handler(request_generating_handler)
    client1.register_req_queued_handler(request_queued_handler)
    client1.register_con_error_handler(connection_error_handler)
    
    # Running client in existing loop
    loop = asyncio.get_running_loop()
    client1.run(loop)

    automatic1111_payload= {
        "prompt": "aloha",
        "steps": 30,
        "cfg_scale": 7,
        "sampler_index": "Euler a",
        "width": 512,
        "height": 768,
        "seed": 1111111111111,
        "hr_scale": 1,
        "hr_upscaler": "Latent",
        "hr_second_pass_steps": 0,
        "hr_resize_x": 768,
        "hr_resize_y": 1024,
        "denoising_strength": 0.7,
        "negative_prompt": "child, childish"
    }

    # Text2img
    kandinsky_payload = {
        "prompt": 'cat girl',
        "steps": 30,
        "guidance_scale": 4, #(1 - Prompt игнорируется; 30 - Четко следовать запросу),
        "height": 512,
        "width": 512,
        "sampler": 'p_sampler',
        "prior_cf_scale": 4,
        "prior_steps": '5',
        "negative_prior_prompt": "",
        "negative_decoder_prompt": ""
    }

    await asyncio.sleep(10)
    
    # СМЕШИВАНИЕ КАРТИНОК
    with open("1.png", "rb") as image:
        f1 = base64.b64encode(image.read())
        f1 = f1.decode('ascii')
    with open("2.png", "rb") as image:
        f2 = base64.b64encode(image.read())
        f2 = f2.decode('ascii')
    mix2img_payload = {
        "images_texts": ['first prompt', f1, f2, 'second prompt'],
        "weights": [0.25, 0.25, 0.25, 0.25],
        "steps": 30,
        "guidance_scale": 4,
        "height": 512,
        "width": 512,
        "sampler": 'p_sampler',
        "prior_cf_scale": 4,
        "prior_steps": '5',
        "negative_prior_prompt": "",
        "negative_decoder_prompt": ""
    }
    await client1.mix2img(
        executor=Executor.KANDINSKY, 
        premium=randint(0, 1), 
        moderate=randint(0, 1), 
        sync_with_s3=True,
        user_id=2, 
        chat_id=2, 
        message_id=2, 
        payload=mix2img_payload,
        max_user_queue_size=1
    )

    # text2img - automatic
    await client1.text2img(
        executor=Executor.AUTOMATIC1111, 
        premium=randint(0, 1), 
        moderate=randint(0, 1), 
        sync_with_s3=True, 
        user_id=1, 
        chat_id=1, 
        message_id=1, 
        payload=automatic1111_payload, 
        max_user_queue_size=2
    )

    # img2img - automatic
    await client1.img2img(
        executor=Executor.AUTOMATIC1111, 
        premium=randint(0, 1), 
        moderate=randint(0, 1), 
        sync_with_s3=True, 
        user_id=1, 
        chat_id=1, 
        message_id=1, 
        payload=automatic1111_payload, 
        max_user_queue_size=2
    )

    
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()