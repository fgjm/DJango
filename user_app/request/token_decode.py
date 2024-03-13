"""
Vaildación del token - User ID
Last modification: 11-02-2023 - Giovanni Junco
"""
import sys
import jwt
from rest_framework import status
from rest_framework.response import Response
from Users_DRF.settings import SECRET_KEY
from logs import get_error


def get_token_user_id(headers=''):
    """ Si el token es correcto devuelve la info del usuario actual
        Required attributes:
            Authorization: token (str), Bearer <token> en headers o en data   
        Return: 
            response: objeto con la informacion del usuario consulatnte (user_id)"""
    try:
        token = None        
        if "Authorization" in headers:
            token = headers["Authorization"].split(" ")[1]
        if token:
            print('ECRET_KEY',token, SECRET_KEY)
            data=jwt.decode(token, SECRET_KEY, algorithms=["HS256"])        
            if 'user_id' in data:
                return data['user_id']
        return Response({
                "message": "Unauthorized",
                "error": "Authentication Token is missing or user id is not valid"
            }, status=status.HTTP_401_UNAUTHORIZED)
    except:
        return get_error('Token decode',sys.exc_info())    
