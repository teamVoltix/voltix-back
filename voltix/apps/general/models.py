from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now, timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, dni, fullname, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(dni=dni, fullname=fullname, email=email, **extra_fields)
        user.set_password(password)  # This hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, dni, fullname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(dni, fullname, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    # Set the unique identifier for the User model
    USERNAME_FIELD = 'dni'  # This tells Django to use DNI for authentication
    REQUIRED_FIELDS = ['fullname', 'email']

    @property
    def id(self):
        return self.user_id

    def __str__(self):
        return f"{self.fullname} ({self.email})"

class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True) 
    # photo_url = models.URLField(max_length=500, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.fullname}"


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    billing_period_start = models.DateField()  # Fecha de inicio del período de facturación
    billing_period_end = models.DateField()  # Fecha de fin del período de facturación
    data = models.JSONField()  # Datos JSON (por ejemplo, OCR o metadatos)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return f"Invoice {self.id} - User: {self.user.fullname}"
    
    def clean(self):
        super().clean()
        if self.billing_period_start > self.billing_period_end:
            raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")


class Measurement(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    measurement_start = models.DateTimeField(null=True, blank=True) # Fecha y hora de inicio
    measurement_end = models.DateTimeField(null=True, blank=True) # Fecha y hora de inicio
    data = models.JSONField()  # Datos adicionales en formato JSON
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return f"Measurement {self.id} - User: {self.user.fullname} - Start: {self.measurement_start} - End: {self.measurement_end}"


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Campos para relaciones genéricas
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Apunta al tipo de modelo
    object_id = models.PositiveIntegerField()  # ID del objeto relacionado
    content_object = GenericForeignKey('content_type', 'object_id')  # Relación genérica

    # Tipo de notificación
    TYPE_CHOICES = [
        ('alerta', 'Alerta inmediata'),
        ('recomendacion', 'Recomendación'),
        ('recordatorio', 'Recordatorio')
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    def __str__(self):
        return f"Notificación {self.notification_id} - Usuario: {self.user.fullname} - Tipo: {self.get_type_display()}"


class NotificationSettings(models.Model):
    notification_setting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Configuración de cada tipo
    enable_alerts = models.BooleanField(default=True)  # Alertas inmediatas
    enable_recommendations = models.BooleanField(default=True)  # Recomendaciones
    enable_reminders = models.BooleanField(default=True)  # Recordatorios

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración de Notificaciones - Usuario: {self.user.fullname}"


class InvoiceComparison(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)  # Factura relacionada
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)  # Medición relacionada
    comparison_results = models.JSONField()  # Resultados de comparación
    is_comparison_valid = models.BooleanField(default=True) # Nuevo campo
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return f"Comparison {self.id} - User: {self.user.fullname} - Invoice: {self.invoice.id}"

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=128)  # Hashed code
    code_expiration = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)  # Track retry attempts
    created_at = models.DateTimeField(auto_now_add=True)

    def set_verification_code(self, code):
        self.verification_code = make_password(code)

    def check_verification_code(self, code):
        return check_password(code, self.verification_code)

    def is_code_expired(self):
        return now() > self.code_expiration

    def __str__(self):
        return f"Verification for {self.email}"
    
import hashlib


class UploadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  #bytes
    file_hash = models.CharField(max_length=64)  #sSHA256 hash
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.fullname} - {self.file_name} - {self.timestamp}"