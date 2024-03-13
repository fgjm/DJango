from faker import Faker

from user_app.models import User

faker = Faker()

class UserFactory:
    ''' Creates default user for the test'''

    def build_user_JSON(self,userOwner):
        ''' Creates random user data '''
        faker = Faker() 
        return {
            'username': faker.name(),
            'email': faker.email(),
            "password": "developer",
            'userIdentification': str(faker.random_number(digits=11)),
            'userPhone': str(faker.random_number(digits=11)),
            'is_active': True,
            'userOwner':userOwner
        }

    def create_user(self, userOwner=''):
        ''' DRF Tets need database for alias 'default' to crete temporal user, 
            this database will be destroyed upon completion'''          
        user = User.objects.create(**self.build_user_JSON(userOwner))
        user.set_password('developer')
        user.save()
        return user