''' views'''
import sys
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from user_app.models import User
from .serializers import (
    UserUpdateSerializer, UserCreateSerializer, UserListSerializer
)
from logs import get_error
from user_app.request.after_request import redis_get_users, encrypt_user
from user_app.request.token_decode import get_token_user_id
from user_app.request.tasks import background_task, background_delete_redis
from django.core.paginator import Paginator
from .socket import send_socket

from user_app.request.jaeger import tracer

class UserViewSet(viewsets.GenericViewSet):
    ''' rutas CURD para usuarios de auditando.co'''
    model = User
    update_serializer_class = UserUpdateSerializer
    create_serializer_class = UserCreateSerializer
    list_serializer_class = UserListSerializer
    queryset = None

    def get_object(self, pk):
        ''' obtiene info de un usuario po id (pk)'''
        try:
            return get_object_or_404(self.model, pk=pk)
        except:
            return False

    def get_queryset(self, user_owner='', license_id=''):
        ''' filtra usuarios activos'''
        if self.queryset is None:
            self.queryset = self.model.objects\
                            .filter(is_active=True)\
                            .values('id', 'username', 'email', 'userFullName', 'userIdentification', 'userProfessionalCard' ,
                                    'userPhone' , 'userOwner' , 'hash', 'createdAt' , 'modificated')
        return self.queryset

    def list(self, request):
        ''' 
        Returns all users
        
        Required.
            Headers (Authorization: Berarer token): token obtained at login
        '''
        try:
            with tracer.start_as_current_span('Get users auditando.co'):
                print('Get users')
            user_owner=request.GET['user_owner'] if 'user_owner' in request.GET else ''
            license_id=request.GET['license_id'] if 'license_id' in request.GET else ''
            page=int(request.GET['page']) if 'page' in request.GET else 1
            limit=int(request.GET['limit']) if 'limit' in request.GET else 10
            user_id=get_token_user_id(request.headers)
            if not isinstance(user_id, int):
                return user_id
            user_info = redis_get_users(f'USER_ALL{user_id}')            
            user_redis= None
            if not user_info:                
                users = self.get_queryset(user_owner, license_id)
                user_info = self.list_serializer_class(users, many=True).data
                user_redis=f'USER_ALL{user_id}'
            pagination_user=Paginator(user_info, limit)
            page_user=pagination_user.page(page)
            print('User PAG: ',pagination_user.count, user_owner, limit, page )
            return Response({
                        'message': 'transaction_completed',
                        'user_info': page_user.object_list,
                        'after_request': user_redis,
                        'next': (page+1) if page_user.has_next() else None,
                        'previous': (page-1) if page_user.has_previous() else None,
                        'count': pagination_user.count
                    }, status=status.HTTP_200_OK)
        except:                
            return get_error('list, api',sys.exc_info())
        
    def retrieve(self, request, pk=None):
        ''' 
        Returns specific user by id
        
        Required.
            Headers (Authorization: Berarer token): token obtained at login
            url (int): numer user id in url, example: /user/6/
        '''
        try:
            with tracer.start_as_current_span('Specific user auditando.co'):
                print('Get one user')
            user_info = redis_get_users(f'USER_{pk}')            
            user_redis= None
            if not user_info:
                user = self.get_object(pk)
                if not user:
                    return Response({
                        'message': 'user_dont_exist',
                        'error': 'user id do not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                user_info = model_to_dict(user)
                user_redis=f'USER_{pk}'
            return Response({
                    'message': 'transaction_completed',
                    'user_info': [user_info],
                    'after_request': user_redis
                }, status=status.HTTP_200_OK) #Response(user_serializer.data)
        except:            
            return get_error('retrieve, api',sys.exc_info())
    
    def create(self, request):  
        ''' metodo POST: crea un usuario nuevo '''
        try:
            with tracer.start_as_current_span('Create user auditando.co'):
                print('post user')
            if not send_socket(
                        {"socket_on":"license_capacity", "license_id":request.data["license_id"]}
                    ):
                return Response({
                    'message': 'user_limit_reached',
                    'error': 'you need to hire more users for the current license'
                }, status=status.HTTP_400_BAD_REQUEST)
            user_serializer = self.create_serializer_class(data=request.data)
            if user_serializer.is_valid():           
                user_info=model_to_dict(user_serializer.save())
                user_redis=f'USER_{user_info["id"]}'
                user_login= encrypt_user(
                                request.data["email"]+request.data["password"]
                            )
                background_task.delay(
                    f'LOGIN_{user_login}', 
                    user_redis
                )
                return Response({
                    'message': 'Successfully_registered_user',
                    'user_info': user_info,
                    'after_request': user_redis,
                    'send_socket':'update_license_users',
                    'license_id': request.data["license_id"]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'message': 'user_not_saved',
                'error': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return get_error('create, api',sys.exc_info())
    
    def update_login(self, request, user):
        ''' Metodo PUT: actualiza un usuario existente'''
        try:            
            if 'password' in request:
                user_redis=f'USER_{user["id"]}'
                user_login= encrypt_user(
                                user["email"]+request["password"]
                            )
                background_task.delay(
                    f'LOGIN_{user_login}', 
                    user_redis
                )
        except:            
            return get_error('update_login, api',sys.exc_info())
    
    def update(self, request, pk=None):
        ''' Metodo PUT: actualiza un usuario existente'''
        try:
            with tracer.start_as_current_span('Update user auditando.co'):
                print('put user')
            user = self.get_object(pk)
            user_serializer = self.update_serializer_class(user, data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user=model_to_dict(user)                
                self.update_login( request.data, user)
                return Response({
                    'message': 'Successfully_updated_user',
                    'user_info': user,
                    'after_request': 'USER_'+pk
                }, status=status.HTTP_200_OK)
            return Response({
                'message': f'Error: {user_serializer.errors}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except:            
            return get_error('update, api',sys.exc_info())

    def destroy(self, request, pk=None):
        ''' Metodo DELETE: elimina un usuario existente'''
        try:
            with tracer.start_as_current_span('Delete user auditando.co'):
                print('del user')
            user_destroy = self.model.objects.filter(id=pk).update(is_active=False)
            if user_destroy == 1:
                background_delete_redis.delay('USER_'+pk)
                return Response({
                    'message': 'Usuario eliminado correctamente'
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'No existe el usuario que desea eliminar'
            }, status=status.HTTP_404_NOT_FOUND)
        except:            
            return get_error('destroy, api',sys.exc_info())
