''' Models to MariaDB: Users, Users Permissions, Users orders and Users Licenses
    from django.contrib.auth.hashers import make_password
'''

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from simple_history.models import HistoricalRecords

class UserManager(BaseUserManager):
    ''' DOC '''
    def _create_user(self, username, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            username = username,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username,  password=None, **extra_fields):
        ''' DOC '''
        return self._create_user(username,  password, False, False, **extra_fields)

    def create_superuser(self, username,  password=None, **extra_fields):
        ''' DOC '''
        return self._create_user(username, password, True, True, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    """ def __str__(self):
        return f'{self.email} {self.username}' 
    # AbstractBaseUser, PermissionsMixin hacen este metodo
    def set_password(self, raw_password: str ) -> None: 
        return make_password(raw_password) """
    username = models.CharField(max_length = 255, unique = True)
    email = models.EmailField('Correo Electrónico',max_length = 255, unique = True)
    userFullName = models.CharField(
        'Nombres y Apellidos', max_length = 255,
        blank = True, null = True)

    userIdentification = models.IntegerField(
        'Documento Identificación',
        unique = True, null = True)
    userProfessionalCard = models.CharField(
        'Tarjeta profesional', max_length = 20,
        blank = True, null = True)
    userPhone = models.IntegerField('Teléfono', null = True)

    userOwner = models.CharField(max_length = 15, blank = True, null = True, default ='')
    hash = models.CharField(max_length = 255, blank = True, null = True, default ='')
    historical = HistoricalRecords()
    objects = UserManager()

    is_active = models.BooleanField(default = True, null = True)
    is_staff = models.BooleanField(default = False, null = True)
    createdAt = models.DateTimeField( default=timezone.now)
    modificated = models.DateTimeField(blank = True, null = True)

    class Meta:  # pylint: disable=R0903
        ''' DOC '''
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        managed = True

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

class UserLicenses(models.Model):
    ''' DOC '''
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    LicensesId = models.IntegerField('id de licencia', blank = True, null = True)
    createdAt = models.DateTimeField(default=timezone.now)
    modificated = models.DateTimeField(blank = True, null = True)
        
    orders_quantity = models.IntegerField(null=True)
    users_quantity = models.IntegerField(null=True)
    license_name  = models.CharField(null=True, unique=True, max_length=150)    
    pesos_col = models.BigIntegerField(null=True)
    is_active =models.BooleanField(default = True)
    is_banned = models.BooleanField(default = False)
    class Meta:  # pylint: disable=R0903
        ''' DOC '''
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
        managed = True

class UserPermissions(models.Model):
    ''' DOC '''
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    createOrder = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    modificated = models.DateTimeField(blank = True, null = True)
    class Meta:  # pylint: disable=R0903
        ''' DOC '''
        managed = True


class UserOrders(models.Model):
    ''' DOC '''
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    LicensesId = models.ForeignKey(UserLicenses, null=True, on_delete=models.CASCADE)
    orderId = models.IntegerField('id de encargo', blank = True, null = True)
    createdAt = models.DateTimeField(auto_now=True)
    modificated = models.DateTimeField(blank = True, null = True)
    order_name  = models.CharField(max_length = 255, null=True, unique=True)

class FilesOrder(models.Model):
    ''' DOC '''
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    LicensesId = models.ForeignKey(UserLicenses, null=True, on_delete=models.CASCADE)
    orderId = models.ForeignKey(UserOrders, null=True, on_delete=models.CASCADE)
    fileId = models.IntegerField('id de encargo', blank = True, null = True)
    createdAt = models.DateTimeField(auto_now=True)
    modificated = models.DateTimeField(blank = True, null = True)
    file_name  = models.CharField(max_length = 255, null=True, unique=True)
    file_url  = models.CharField(max_length = 255, null=True, unique=True)

class UserNotification(models.Model):
    ''' DOC '''
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    LicensesId = models.ForeignKey(UserLicenses, null=True, on_delete=models.CASCADE)
    orderId = models.ForeignKey(UserOrders, null=True, on_delete=models.CASCADE)
    fileId = models.IntegerField('id de encargo', blank = True, null = True)
    createdAt = models.DateTimeField(auto_now=True)
    modificated = models.DateTimeField(blank = True, null = True)
    