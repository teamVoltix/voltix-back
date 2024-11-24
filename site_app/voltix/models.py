from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    preferences = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.fullname}"


# class Invoice(models.Model):
#     invoice_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     upload_date = models.DateTimeField()
#     amount_due = models.DecimalField(max_digits=10, decimal_places=2)
#     due_date = models.DateField()
#     provider = models.CharField(max_length=150)
#     file_path = models.CharField(max_length=255)
#     ocr_data = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Factura {self.invoice_id} - Usuario: {self.user.fullname}"


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



# Esta tabla creemos que no va... ya que serviria para refistrar mediciones que es algo que la app ni la empresa hacen de momento.
# class Measurement(models.Model):
#     measurement_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateTimeField()
#     value = models.DecimalField(max_digits=10, decimal_places=2)
#     type = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Medición {self.measurement_id} - Usuario: {self.user.fullname}"

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
        return f"Measurement {self.id} - User: {self.user.fullname} - Date: {self.date}"



class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación {self.notification_id} - Usuario: {self.user.fullname}"


# El usuario podra desactivar las notificaciones si lo desea
class NotificationSettings(models.Model):
    notification_setting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Configuración de Notificación {self.type} - Usuario: {self.user.fullname}"


# class InvoiceComparison(models.Model):
#     comparison_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     invoice1 = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='comparison_invoice1')
#     invoice2 = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='comparison_invoice2')
#     comparison_date = models.DateTimeField()
#     comparison_result = models.JSONField()

#     def __str__(self):
#         return f"Comparación {self.comparison_id} - Usuario: {self.user.fullname}"

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
    