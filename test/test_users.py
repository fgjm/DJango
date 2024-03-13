
from rest_framework import status
from test.test_setup import TestSetUp
from .factories import UserFactory

class UsersTestCase(TestSetUp):
    url = '/users/'

    def test_get_list(self):
        user_list = UserFactory().create_user(self.userOwner)
        response = self.client.get(
            self.url,            
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('test_get_list:',response,response.data, user_list)
        
    def test_get_one_user(self):        
        response = self.client.get(
            f'{self.url}{self.userOwner}/',            
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('test_get_one_user:',response,response.data)
    
    def test_user_not_found(self):        
        response = self.client.get(
            f'{self.url}3/',            
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print('test_user_not_found:',response,response.data)
    
    def test_create_user(self):
        new_user = UserFactory().build_user_JSON(self.userOwner)
        response = self.client.post(
            self.url,   new_user,         
            format='json'
        )
        print(' -test_create_user:',response,response.data, new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
