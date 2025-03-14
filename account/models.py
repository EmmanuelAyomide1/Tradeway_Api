from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import random
import datetime
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Account(AbstractUser):
    ACCOUNT_TYPES = [
        ('ADMIN', 'Admin'),
        ('SELLER', 'Seller'),
        ('BUYER', 'Buyer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Otp(models.Model):
    otp = models.CharField(max_length=4)
    user = models.ForeignKey('Account', on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.otp} - {self.user.email}"

    @classmethod
    def generate_otp(cls, user, expiry_minutes=10):
        """
        Generate a new OTP for the given user
        """
        # Invalidate existing unused OTPs for this user and purpose
        cls.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Generate a new OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        expires_at = timezone.now() + datetime.timedelta(minutes=expiry_minutes)
        
        # Create and save new OTP
        otp_obj = cls.objects.create(
            otp=otp_code,
            user=user,
            expires_at=expires_at
        )
        
        return otp_obj
    
    def is_valid(self):
        """
        Check if the OTP is valid (not expired and not used)
        """
        return not self.is_used and self.expires_at > timezone.now()
    
    def use(self):
        """
        Mark the OTP as used
        """
        self.is_used = True
        self.save(update_fields=['is_used', 'updated_at'])
        
    @classmethod
    def verify_otp(cls, user, otp_code):
        """
        Verify an OTP for a user and mark it as used if valid
        """
        try:
            otp_obj = cls.objects.get(
                user=user,
                otp=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            otp_obj.use()
            return True
        except cls.DoesNotExist:
            return False