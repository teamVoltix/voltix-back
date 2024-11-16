from django.db import models

class Usuario(models.Model):
    user_id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return {
            self.email,
            self.fullname
            }


class Perfil(models.Model):
    profile_id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=150)
    birth_date = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    preferences = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.fullname}"

class Factura(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    upload_date = models.DateTimeField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    provider = models.CharField(max_length=150)
    file_path = models.CharField(max_length=255)
    ocr_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Factura {self.invoice_id} - Usuario: {self.user.username}"

# Esta tabla creemos que no va... ya que serviria para refistrar mediciones que es algo que la app ni la empresa hacen de momento.
class Medicion(models.Model):
    measurement_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medición {self.measurement_id} - Usuario: {self.user.username}"

class Notificacion(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación {self.notification_id} - Usuario: {self.user.username}"

# El usuario pobra desactivar las notificaciones si lo desea
class ConfiguracionNotificaciones(models.Model):
    notification_setting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Configuración de Notificación {self.type} - Usuario: {self.user.username}"

class ComparacionFacturas(models.Model):
    comparison_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    invoice1 = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='comparison_invoice1')
    invoice2 = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='comparison_invoice2')
    comparison_date = models.DateTimeField()
    comparison_result = models.JSONField()

    def __str__(self):
        return f"Comparación {self.comparison_id} - Usuario: {self.user.username}"
    

class BaseMiLuz(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    expected_consumption = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_kwh = models.DecimalField(max_digits=10, decimal_places=4)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_expected_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"BaseMiLuz ID: {self.id} - Cliente: {self.client.username}"

    