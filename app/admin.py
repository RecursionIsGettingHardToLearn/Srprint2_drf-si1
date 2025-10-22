from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Rol, Administrativo, Instructor, Nutricionista,
    Cliente, Antecedentes, Seguimiento, Rutina, Ejercicio, DetalleRutina,
    Disciplina, Sala, Horario, Reserva, Suscripcion, Promocion, Pago,
  Bitacora, DetalleBitacora
)

# Configuración personalizada para Usuario
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefono', 'sexo', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'sexo')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('telefono', 'sexo', 'direccion', 'fecha_nacimiento')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('telefono', 'sexo', 'direccion', 'fecha_nacimiento')
        }),
    )

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)



@admin.register(Administrativo)
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'turno')
    list_filter = ('cargo', 'turno')
    search_fields = ('usuario__username', 'cargo')

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'fecha_ingreso')
    list_filter = ('especialidad', 'fecha_ingreso')
    search_fields = ('usuario__username', 'especialidad')
    date_hierarchy = 'fecha_ingreso'

@admin.register(Nutricionista)
class NutricionistaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'horario_atencion', 'fecha_titulacion')
    list_filter = ('fecha_titulacion',)
    search_fields = ('usuario__username',)
    date_hierarchy = 'fecha_titulacion'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'suscripcion_actual', 'fecha_ini_mem', 'fecha_fin_mem')
    list_filter = ('suscripcion_actual', 'fecha_ini_mem', 'fecha_fin_mem')
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'fecha_ini_mem'

@admin.register(Antecedentes)
class AntecedentesAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'nutricionista', 'fecha', 'peso', 'altura', 'imc', 'fecha_prox_consulta')
    list_filter = ('fecha', 'nutricionista')
    search_fields = ('cliente__usuario__username', 'nutricionista__usuario__username', 'diagnostico')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'instructor', 'fecha', 'prior_seg')
    list_filter = ('fecha', 'instructor', 'prior_seg')
    search_fields = ('cliente__usuario__username', 'instructor__usuario__username', 'objetivo')
    date_hierarchy = 'fecha'

@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'seguimiento', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('seguimiento__instructor',)

@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')

@admin.register(DetalleRutina)
class DetalleRutinaAdmin(admin.ModelAdmin):
    list_display = ('rutina', 'ejercicio', 'dia', 'series', 'repeticiones', 'peso')
    list_filter = ('dia', 'rutina')
    search_fields = ('rutina__nombre', 'ejercicio__nombre')

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('capacidad',)

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('capacidad',)

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'sala', 'instructor', 'dia', 'hora_ini', 'hora_fin', 'cupo')
    list_filter = ('dia', 'disciplina', 'sala', 'instructor')
    search_fields = ('disciplina__nombre', 'sala__nombre', 'instructor__usuario__username')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'horario', 'fecha', 'estado')
    list_filter = ('estado', 'fecha', 'horario__disciplina')
    search_fields = ('cliente__usuario__username', 'horario__disciplina__nombre')
    date_hierarchy = 'fecha'

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'precio', 'descripcion')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descuento', 'fecha_ini', 'fecha_fin', 'estado')
    list_filter = ('estado', 'tipo', 'fecha_ini', 'fecha_fin')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_ini'

class PagoAdmin(admin.ModelAdmin):
    readonly_fields = ('fecha_pago', 'monto', 'metodo_pago')

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'login', 'logout', 'ip', 'device')
    list_filter = ('login', 'logout')
    search_fields = ('usuario__username', 'ip', 'device')
    date_hierarchy = 'login'
    readonly_fields = ('login', 'logout', 'usuario', 'ip', 'device')

@admin.register(DetalleBitacora)
class DetalleBitacoraAdmin(admin.ModelAdmin):
    list_display = ('bitacora', 'accion', 'fecha', 'tabla')
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = ('bitacora__usuario__username', 'accion', 'tabla')
    date_hierarchy = 'fecha'
    readonly_fields = ('bitacora', 'accion', 'fecha', 'tabla')