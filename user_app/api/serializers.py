''' Serializer CURD Users'''
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user_app.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ @classmethod
    def get_token(cls, user):
        print('AA:',user) """
    pass


class CustomUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('password', 'groups', "user_permissions")

class UserCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
    
    def create(self,validated_data):
        user = User(**validated_data)        
        user.set_password(validated_data['password']) #user.password=user.set_password(validated_data['password'])
        user.hash = hex(hash(validated_data['username']))[2:]
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True, required=False
    )
    password_confirm = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    class Meta:
        model = User
        fields = '__all__'    
    
    def update(self, instance, validated_data):
        updated_user= super().update(instance, validated_data)
        
        if 'password' in validated_data:
            if validated_data['password'] != validated_data['password_confirm']:
                raise serializers.ValidationError(
                    {'password':'Debe ingresar ambas contraseñas iguales'}
                )
            print('*a')
            updated_user.set_password(validated_data['password'])
        updated_user.save()
        print('Update serializer:', updated_user)
        return updated_user

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'groups', "user_permissions")   

    def to_representation(self, instance):
        
        return instance


