from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.contrib import auth
# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self, email, name, phone, password,is_active=True, is_staff=False):
        if not email:
            raise ValueError("Email is must")
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            is_active=is_active,
            is_staff=is_staff
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError("Email is must")
        user = self.model(
        email=self.normalize_email(email),
        password=password,)
        user.set_password(user.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=10, unique=True, null=True)
    date_joined = models.TimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)
    

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True




class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=225)
    address1 = models.TextField(max_length=250)
    country = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zip = models.IntegerField()