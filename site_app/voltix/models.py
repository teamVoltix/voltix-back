from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    photo_url = models.URLField(max_length=500, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.fullname}"


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    billing_period_start = models.DateField()  # Fecha de inicio del período de facturación
    billing_period_end = models.DateField()  # Fecha de fin del período de facturación
    # price_per_kwh = models.DecimalField(max_digits=10, decimal_places=4)  # Precio por kWh
    data = models.JSONField()  # Datos JSON (por ejemplo, OCR o metadatos)
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return f"Invoice {self.id} - User: {self.user.fullname}"


class Measurement(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    measurement_start = models.DateTimeField(null=True, blank=True) # Fecha y hora de inicio
    measurement_end = models.DateTimeField(null=True, blank=True) # Fecha y hora de inicio
    # value = models.DecimalField(max_digits=10, decimal_places=2)  # Valor de la medición (kWh, por ejemplo)
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

    def __str__(self):
        return f"Configuración de Notificaciones - Usuario: {self.user.fullname}"


class InvoiceComparison(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)  # Factura relacionada
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)  # Medición relacionada
    # comparison_date = models.DateField()  # Fecha de comparación, derivada del período de consumo de la factura
    comparison_results = models.JSONField()  # Resultados de comparación
    is_comparison_valid = models.BooleanField(default=True) # Nuevo campo
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización


    # def save(self, *args, **kwargs):
    #     # Extraer la fecha del período de consumo de la factura al guardar
    #     if self.invoice:
    #         self.comparison_date = self.invoice.billing_period_start  # Ajustar según la lógica
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Comparison {self.id} - User: {self.user.fullname} - Invoice: {self.invoice.id}"



class MiLuzBase(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    expected_consumption = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_kwh = models.DecimalField(max_digits=10, decimal_places=4)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_expected_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"BaseMiLuz ID: {self.id} - Usuario: {self.user.fullname}"


class Token(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return now() < self.expires_at

    def __str__(self):
        return f"Token for {self.user.fullname} (valid: {self.is_valid()})"
