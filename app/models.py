# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
#pago
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
#core exception
from django.core.exceptions import ValidationError
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre
class Usuario(AbstractUser):
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True) 
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username



class Administrativo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, related_name='administrativo')
    cargo = models.CharField(max_length=100)
    turno = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Administrativo"
        verbose_name_plural = "Administrativos"

    def __str__(self):
        return f"Admin: {self.usuario.username}"

class Instructor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, related_name='instructor')
    especialidad = models.CharField(max_length=100)
    fecha_ingreso = models.DateField(auto_now_add=True) # Campo añadido, no estaba en el ER pero es común

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructores"

    def __str__(self):
        return f"Instructor: {self.usuario.username} ({self.especialidad})"

class Nutricionista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, related_name='nutricionista')
    horario_atencion = models.CharField(max_length=255, blank=True, null=True)
    fecha_titulacion = models.DateField(blank=True, null=True) # Campo añadido

    class Meta:
        verbose_name = "Nutricionista"
        verbose_name_plural = "Nutricionistas"

    def __str__(self):
        return f"Nutricionista: {self.usuario.username}"

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, related_name='cliente')
    suscripcion_actual = models.ForeignKey('Suscripcion', on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes_activos')
    fecha_ini_mem = models.DateField(blank=True, null=True) # Fecha inicio membresía
    fecha_fin_mem = models.DateField(blank=True, null=True) # Fecha fin membresía

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"Cliente: {self.usuario.username}"

class Antecedentes(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='antecedentes')
    nutricionista = models.ForeignKey(Nutricionista, on_delete=models.SET_NULL, null=True, blank=True, related_name='antecedentes_registrados')
    fecha = models.DateField()
    diagnostico = models.TextField(blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    altura = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    imc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    gc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # Grasa Corporal
    cc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # Circunferencia de Cintura
    fecha_prox_consulta = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Antecedente"
        verbose_name_plural = "Antecedentes"
        ordering = ['-fecha'] # Últimos antecedentes primero

    def __str__(self):
        return f"Antecedente de {self.cliente.usuario.username} ({self.fecha})"

class Seguimiento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='seguimientos')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name='seguimientos_impartidos')
    fecha = models.DateField()
    objetivo = models.TextField(blank=True, null=True)
    prior_seg = models.CharField(max_length=100, blank=True, null=True) # Prioridad de seguimiento
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Seguimiento de {self.cliente.usuario.username} ({self.fecha})"

class Rutina(models.Model):
    seguimiento = models.ForeignKey(Seguimiento, on_delete=models.CASCADE, related_name='rutinas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"

    def __str__(self):
        return self.nombre

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"

    def __str__(self):
        return self.nombre

class DetalleRutina(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='detalles')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='detalles_rutina')
    dia = models.CharField(max_length=20) # Lunes, Martes, etc.
    series = models.IntegerField()
    repeticiones = models.IntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = "Detalle de Rutina"
        verbose_name_plural = "Detalles de Rutina"
        unique_together = ('rutina', 'ejercicio', 'dia') # Un ejercicio puede estar en un día específico de una rutina

    def __str__(self):
        return f"{self.rutina.nombre} - {self.ejercicio.nombre} ({self.dia})"

class Disciplina(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    capacidad = models.IntegerField(default=1) # Capacidad máxima de la disciplina

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return self.nombre

class Sala(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    capacidad = models.IntegerField()

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return self.nombre

class Horario(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='horarios')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='horarios')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name='horarios_impartidos')
    dia = models.CharField(max_length=20) # Lunes, Martes, etc.
    hora_ini = models.TimeField()
    hora_fin = models.TimeField()
    cupo = models.IntegerField(default=0) # Número de cupos disponibles en ese horario

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        unique_together = ('disciplina', 'dia', 'hora_ini', 'sala') # Para evitar conflictos de horario en la misma sala

    def __str__(self):
        return f"{self.disciplina.nombre} - {self.dia} ({self.hora_ini}-{self.hora_fin}) en {self.sala.nombre}"

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='Pendiente') # Ej: Pendiente, Confirmada, Cancelada

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        unique_together = ('cliente', 'horario') # Un cliente solo puede reservar una vez un horario específico

    def __str__(self):
        return f"Reserva de {self.cliente.usuario.username} para {self.horario.disciplina.nombre} el {self.horario.dia} a las {self.horario.hora_ini}"

class Suscripcion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)  # Ej: Mensual, Trimestral, Anual
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return self.nombre


    
class SuscripcionCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='suscripciones')
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE)
    estado_pago = models.BooleanField(default=False)  # Estado del pago para este cliente
    fecha_inicio = models.DateField()  # Fecha de inicio de la suscripción
    fecha_fin = models.DateField()  # Fecha de fin de la suscripción
    fecha_pago = models.DateField(blank=True, null=True)  # Fecha de pago, si ya ha pagado

    class Meta:
        unique_together = ('cliente', 'suscripcion')  # Un cliente solo puede tener una suscripción activa de cada tipo
        verbose_name = "Suscripción Cliente"
        verbose_name_plural = "Suscripciones Clientes"

    def __str__(self):
        return f"Suscripción de {self.cliente.usuario.username} a {self.suscripcion.nombre}"


class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True, null=True) # Ej: Descuento, 2x1
    estado = models.BooleanField(default=False) # Activa/Inactiva
    descripcion = models.TextField(blank=True, null=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # Porcentaje o monto fijo
    fecha_ini = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"

    def __str__(self):
        return self.nombre

class Pago(models.Model):
    TIPO_PAGO_CHOICES = [
          ('suscripcion', 'Suscripción'),
    ('promocion', 'Promoción'),
    ]

    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo'),
        ('qr', 'Pago QR'),
    ]

    # Relación directa con el usuario que realizó el pago
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos',
        help_text="Usuario que realizó el pago"
    )

    # Tipo de pago para filtrado rápido
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES,default='suscripcion')

    # Monto y detalles del pago
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="N° de transacción, comprobante, etc.")
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')


    def __str__(self):
        return f"{self.get_tipo_pago_display()} - {self.monto} - {self.fecha_pago.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    

class Bitacora(models.Model):
    login = models.DateTimeField()
    logout = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(null=True, blank=True, help_text="Dirección IPv4 o IPv6 del dispositivo")
    device = models.CharField(max_length=255, null=True, blank=True, help_text="Ubicación aproximada (p.ej. 'Ciudad, País' o 'lat,lon')")
    class Meta: db_table = 'bitacora'

class DetalleBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='detallebitacoras')
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    tabla = models.CharField(max_length=50)
    class Meta: db_table = 'detallebitacora'