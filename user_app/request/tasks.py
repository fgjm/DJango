# tasks.py
from celery import shared_task
import time

from .redis import RedisClass
from user_app.api.socket import send_socket

@shared_task
def background_task(id, data) -> str:    
    user_redis = RedisClass(id)
    res=user_redis.set(data) 
    return 'background_task_succeeded'

@shared_task
def background_delete_redis(id) -> str:    
    user_redis = RedisClass(id)
    res=user_redis.delete()  
    return 'background_delete_redis'

@shared_task
def background_send_socket(route,license_id) -> str:
    print('B')  
    respose_socket = send_socket(
                        {"socket_on":route, "license_id":license_id}
                    )
    print('background_send_socket:',respose_socket)
    return 'background_send_socket'