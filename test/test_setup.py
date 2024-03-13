''' TEST '''
import sys
import pdb # paracer trace o debug
from faker import Faker

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import UserFactory
from logs import get_error

class TestSetUp(APITestCase):    

    def setUp(self):
        ''' initial setup: crete user, login and make token '''
        try:
            self.user = UserFactory().create_user()
            response = self.client.post(
                '/login/',   
                {
                    "email":self.user.email,
                    "password": "developer"
                    },
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK) # metodo verifica dos valores
            self.token = response.data['access_token']
            self.userOwner = response.data['user_info']['id']
            #pdb.set_trace() #para la ejecucion. se puede digitar ejemplo: respose.data para ver los valores, c para continuar
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
            return super().setUp()
        except KeyError:
            return get_error('setUp, test',sys.exc_info())
