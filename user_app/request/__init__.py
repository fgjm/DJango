''' Middleware: berore_request , request and afterrequest'''
import sys
from logs import get_error
from .tasks import background_task, background_send_socket

# middlewares.py
class BeforeRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response    

    def after_request(self, id, data):
        if id:     
            background_task.delay(id, data)
    
    def send_socket(self, route, data):        
        background_send_socket.delay(route, data)

    def __call__(self, request):
        ''' DOC '''
        try:           
            response = self.get_response(request)    
            if hasattr(response, 'data'):
                if 'after_request' in  response.data:
                    self.after_request(response.data['after_request'], response.data['user_info'])        
                if 'send_socket' in  response.data:
                    self.send_socket(response.data['send_socket'], response.data['license_id'])  
            return response
        except:
            return get_error(request.path+', Before request',sys.exc_info())
