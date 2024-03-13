"""
Errors 500
Last modification: 24-04-2023 - Giovanni Junco
"""
from .logs import logging
from rest_framework import status
from rest_framework.response import Response


def do_log(tipo, messaje, from_log,type_log):
    log=f'{tipo} - Where: {messaje}'
    log+=f' Line: {from_log}'
    if type_log=='info':
        logging.info(log)
    elif type_log=='error':
        logging.error(log)
    elif type_log=='critical':
        logging.critical(log)
    elif type_log=='warning':
        logging.warning(log)



def get_error(point,error):
    """ log and response error handling 500
        Required attributes:
            point (String): endpoint or resolve
            error(object): data error
        Return: 
            response: to graphql
    """
    do_log(str(error),point,
            error[2].tb_lineno
            ,'error')
    return Response({
                'message': 'internal_error', 
                'error':f'Point: {point} - Error: {error}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
