import sys
import redis
import json

from logs import get_error

redis_server = redis.Redis(host="localhost",port="6379")

class RedisClass:
    def __init__(redis_object, id):
        redis_object.id = id
    
    def clear_all(redis_object):
        try:
            list_key_redis =list(redis_server.scan_iter('USER_*'))
            redis_size = redis_server.dbsize()
            if  len(list_key_redis) > 30 or redis_size > 10:
                redis_server.flushdb()
            return True
        except:
            get_error('clear, redis',sys.exc_info())
        return False

    def set(redis_object, data):
        try:
            redis_object.clear_all()       
            if isinstance(data, list):
                data = '|*'.join([json.dumps(dt, indent=4, sort_keys=True, default=str) for dt in data]) 
            else:
                data = json.dumps(data, indent=4, sort_keys=True, default=str)
            redis_server.mset({redis_object.id: data })
            return True
        except:
            get_error('set, redis',sys.exc_info())
        return False

    def get(redis_object):
        try:   
            if redis_server.exists(redis_object.id)!=0:                
                result_redis=redis_server.get(redis_object.id).decode("utf-8").split('|*')                
                if len(result_redis)>1:
                    result_redis=[json.loads(data) for data in result_redis]
                else:
                    result_redis=json.loads(result_redis[0])                
                return result_redis
        except:
            get_error('get, redis',sys.exc_info())
        return False

    def delete(redis_object):
        try:
            redis_server.delete(redis_object.id)
            return True
        except:
            get_error('delete, redis',sys.exc_info())
        return False
