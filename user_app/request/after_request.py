''' methods to execute after request '''
import sys
import hashlib
from .redis import RedisClass
from logs import get_error


def encrypt_user(user_data):
        try:
            return hashlib.new("sha1", user_data.encode()).hexdigest()
        except:
            get_error('encrypt_user, after_request',sys.exc_info())
        return user_data

def redis_get_login( mail, password):
        ''' validates if the user exists in REDIS
            
            Return
                redis_id and user data '''
        return RedisClass(
                f'LOGIN_{encrypt_user(mail+password)}'
            ).get()        

def redis_get_users( id_redis):
        ''' validates if the user exists in REDIS
            
            Return
                redis_id and user data '''
        return RedisClass(
                id_redis
            ).get()