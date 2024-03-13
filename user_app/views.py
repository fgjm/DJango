''' Class Login user and logout'''
import sys

from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session


from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from logs import get_error, do_log
from .api.serializers import CustomTokenObtainPairSerializer, CustomUserSerializer
from .models import User

from .request.tasks import background_task
from .request.after_request import encrypt_user,\
    redis_get_users, redis_get_login
from user_app.request.jaeger import tracer

class Login(TokenObtainPairView):
    ''' User Authentication Object '''
    serializer_class = CustomTokenObtainPairSerializer

    def authenticate(self, username=None, password=None):
        ''' valid user email and password'''
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            user=None
        if user:
            if user.check_password(password):
                if not user.is_active:
                    return Response(
                        {'message': 'user_cannot_login'},
                        status=status.HTTP_400_BAD_REQUEST
                        )
                return user
        return Response(
            {'message': 'incorrect_username_password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def close_sessions(self, user):
        ''' close all open sessions'''
        all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
        if all_sessions.exists():
            for session in all_sessions:
                session_data = session.get_decoded()
                if user == int(session_data.get('_auth_user_id')):
                    session.delete()

    def make_token(self, username, password):
        ''' Create token access and refersh
        '''
        try:
            login_serializer = self.serializer_class(
                                data={"username":username, "password":password}
                            )
            if not login_serializer.is_valid():
                return Response(
                    {'message': 'incorrect_username_password'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return {'access_token': login_serializer.validated_data.get('access'),
                    'refresh_token': login_serializer.validated_data.get('refresh')}
        except KeyError:
            return get_error('make_token, views',sys.exc_info())

    def post(self, request): # pylint: disable=W0221
        ''' POST receive request /login/

        Required request.
            - email (str): char field unique of model User
            - password (str): char field min length 6 of api, UserCreateSerializer
        Returns.
            - access_token (str): required to access microservices
            - refresh_token (str): required to update access_token
            - user_info (dict): user data in model User
            - message (str): code response to i18n
            - status (int): status codes num'''
        try:
            with tracer.start_as_current_span('Login auditando.co'):
                print('Login')
            password = request.data.get('login_password', '')
            email=request.data.get('login_user', '')
            user_login=redis_get_login( email, password)
            user_info = redis_get_users(user_login) if user_login else None
            print('user_info:',user_info)
            do_log(user_info,user_login,
                email ,'info')
            user_redis= None
            if not user_info:
                user = self.authenticate(email, password)
                print('Login:', user, isinstance(user, User), email, password)
                if not isinstance(user, User):
                    return user
                user_info = CustomUserSerializer(user).data
                user_redis = f'USER_{user.id}'
                self.close_sessions(user.id)
                background_task.delay(
                    f'LOGIN_{encrypt_user(email+password)}',
                    user_redis
                )
            token = self.make_token(user_info['username'], password)
            if not isinstance(token, dict):
                return token
            data_send={ 'user_info': [user_info], 'message': 'successful_login',
                        'after_request': user_redis, 'token_info':token }
            #data_send.update(token)
            return Response(data_send, status=status.HTTP_200_OK)
        except KeyError:
            return get_error('Post Login., views',sys.exc_info())

class Logout(GenericAPIView):
    ''' Close app'''
    def post(self, request):
        ''' add refresh token to blacklist'''
        with tracer.start_as_current_span('Logout auditando.co'):
                print('Logout')
        user = User.objects.filter(id=request.data.get('user', 0))
        if user.exists():
            token=RefreshToken(request.data.get('refresh', ''))
            token.blacklist()
            return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
        return Response({'message': 'user_not_exist'}, status=status.HTTP_400_BAD_REQUEST)
