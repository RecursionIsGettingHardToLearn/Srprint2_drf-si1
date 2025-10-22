# serializers.py

from rest_framework import serializers
from .models import (
    Usuario, Rol, Administrativo, Instructor, Nutricionista,
    Cliente, Antecedentes, Seguimiento, Rutina, Ejercicio, DetalleRutina,
    Disciplina, Sala, Horario, Reserva, Suscripcion, Promocion, Pago,
    Bitacora, DetalleBitacora,SuscripcionCliente
)
from rest_framework.exceptions import AuthenticationFailed
#pago
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

# --- Serializadores para Modelos Base / Sin muchas relaciones de entrada ---

class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido_paterno', 'apellido_materno',
            'sexo', 'direccion', 'fecha_nacimiento', 'rol', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True,'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)  # ✅ ESTO HASHEA LA CONTRASEÑA
        user.save()
        return user
    def update(self, instance, validated_data):
        # 1. Handle password separately
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # 2. Call super().update() for other fields
        # This will update all fields present in validated_data
        updated_instance = super().update(instance, validated_data)
        
        # 3. Save the instance if password was changed
        if password:
            updated_instance.save() # Save only if password was updated, otherwise super().update might have saved.
                                   # More robust: always save at the end if you perform a set_password.
        
        return updated_instance
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['rol_nombre'] = instance.rol.nombre if instance.rol else None
        return rep
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

class DisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = '__all__'

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información relacionada
    usuario_nombre = serializers.SerializerMethodField()
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    
    # Campos para el objeto genérico relacionado
    objeto_relacionado_tipo = serializers.SerializerMethodField()
    objeto_relacionado_id = serializers.SerializerMethodField()
    objeto_relacionado_descripcion = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            'id', 'usuario', 'usuario_nombre', 'tipo_pago', 'tipo_pago_display',
            'monto', 'fecha_pago', 'metodo_pago', 'metodo_pago_display',
            'referencia', 'comprobante', 'observaciones',
            'objeto_relacionado_tipo', 'objeto_relacionado_id', 'objeto_relacionado_descripcion'
        ]
        read_only_fields = ['fecha_pago', 'comprobante']  # El comprobante se genera por la señal

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f"{obj.usuario.nombre} {obj.usuario.apellido_paterno}".strip()
        return None
    
    def get_objeto_relacionado_tipo(self, obj):
        if obj.content_object:
            return obj.content_object._meta.verbose_name
        return None

    def get_objeto_relacionado_id(self, obj):
        if obj.content_object:
            return obj.content_object.id
        return None
        
    def get_objeto_relacionado_descripcion(self, obj):
        if obj.content_object:
            # Aquí puedes personalizar cómo quieres describir cada tipo de objeto.
            # Para Cuota
            if isinstance(obj.content_object, Suscripcion):
                return f"Suscripción {obj.content_object.nombre} - {obj.content_object.tipo} - ${obj.content_object.precio}"
            # Para Promoción
            elif isinstance(obj.content_object, Promocion):
                return f"Promoción {obj.content_object.nombre} - {obj.content_object.descuento}% de descuento"
            # Añadir más casos si tienes otros tipos de objetos relacionados
            return str(obj.content_object)  # Fallback a la representación por defecto del objeto
        return None

    def create(self, validated_data):
        # Si el tipo de pago es 'cuota', 'reserva', 'suscripcion' o 'promocion', asegúrate de que el content_object
        # y content_type se asignen correctamente.
        tipo_pago = validated_data.get('tipo_pago')
        content_object = validated_data.pop('content_object', None)  # Extraer si se pasó en validated_data

        if content_object:
            validated_data['content_type'] = ContentType.objects.get_for_model(content_object)
            validated_data['object_id'] = content_object.id
        elif tipo_pago in ['suscripcion', 'promocion'] and not (validated_data.get('content_type') and validated_data.get('object_id')):
            # Si es un pago de cuota, reserva, suscripción o promoción, y no se proporcionó el objeto genérico,
            # deberías validar que se asigne correctamente, o lanzar un error.
            # Para este ejemplo, lo dejaremos pasar, asumiendo que el frontend o Stripe lo gestiona.
            pass  # Aquí puedes añadir lógica de validación más estricta si es necesario

        return super().create(validated_data)


class PromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocion
        fields = '__all__'


class AdministrativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrativo
        fields = ['usuario', 'cargo', 'turno'] # 'usuario' es la PK aquí

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.usuario:
            representation['usuario_username'] = instance.usuario.username
        return representation

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['usuario', 'especialidad', 'fecha_ingreso'] # 'usuario' es la PK aquí

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.usuario:
            representation['usuario_username'] = instance.usuario.username
        return representation

class NutricionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutricionista
        fields = ['usuario', 'horario_atencion', 'fecha_titulacion'] # 'usuario' es la PK aquí

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.usuario:
            representation['usuario_username'] = instance.usuario.username
        return representation

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['usuario', 'suscripcion_actual', 'fecha_ini_mem', 'fecha_fin_mem'] # 'usuario' es la PK aquí

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.usuario:
            representation['usuario_username'] = instance.usuario.username
        if instance.suscripcion_actual:
            representation['suscripcion_actual_nombre'] = instance.suscripcion_actual.nombre
        return representation

class AntecedentesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antecedentes
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.cliente:
            representation['cliente_username'] = instance.cliente.usuario.username
        if instance.nutricionista:
            representation['nutricionista_username'] = instance.nutricionista.usuario.username
        return representation

class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.cliente:
            representation['cliente_username'] = instance.cliente.usuario.username
        if instance.instructor:
            representation['instructor_username'] = instance.instructor.usuario.username
        return representation

class RutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rutina
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.seguimiento:
            representation['seguimiento_cliente_username'] = instance.seguimiento.cliente.usuario.username
            representation['seguimiento_fecha'] = instance.seguimiento.fecha
        return representation

class DetalleRutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleRutina
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.rutina:
            representation['rutina_nombre'] = instance.rutina.nombre
        if instance.ejercicio:
            representation['ejercicio_nombre'] = instance.ejercicio.nombre
        return representation

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.disciplina:
            representation['disciplina_nombre'] = instance.disciplina.nombre
        if instance.sala:
            representation['sala_nombre'] = instance.sala.nombre
        if instance.instructor:
            representation['instructor_username'] = instance.instructor.usuario.username
        return representation

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.cliente:
            representation['cliente_username'] = instance.cliente.usuario.username
        if instance.horario:
            representation['horario_disciplina_nombre'] = instance.horario.disciplina.nombre
            representation['horario_dia'] = instance.horario.dia
            representation['horario_hora_ini'] = instance.horario.hora_ini
        return representation





class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.usuario:
            representation['usuario_username'] = instance.usuario.username
        return representation

class DetalleBitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleBitacora
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.bitacora:
            representation['bitacora_login_time'] = instance.bitacora.login
            representation['bitacora_usuario_username'] = instance.bitacora.usuario.username if instance.bitacora.usuario else None
        return representation

class MyTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):#@
        username=attrs.get(self.username_field) or attrs.get('username')
        password=attrs.get('password')
        User=get_user_model()
        user=User.objects.filter(username=username).first()
        print(user)
        if not user:
            raise AuthenticationFailed('el usuario no existe')
        if not user.check_password(password):
            raise AuthenticationFailed('ingrese su contrase;a correctemetn')
        
            
        return super().validate(attrs)
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()


# --- NUEVOS SERIALIZADORES PARA EL ENDPOINT `usuario/me` ---

class RolMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre'] # Solo id y nombre del rol

class UsuarioMeSerializer(serializers.ModelSerializer):
    rol = serializers.StringRelatedField()  # This will get the `nombre` of the Rol
    class Meta:
        model = Usuario
        # Incluye todos los campos de Usuario más el perfil anidado
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido_paterno',
            'telefono', 'sexo', 'direccion', 'fecha_nacimiento', 'rol','apellido_materno'
        ]
class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = ['id', 'nombre', 'tipo', 'descripcion', 'precio']

class SuscripcionClienteSerializer(serializers.ModelSerializer):
    suscripcion = SuscripcionSerializer()  # Anidar el serializer de Suscripción
    cliente = serializers.StringRelatedField()  # Relacionar con el nombre de usuario del cliente

    class Meta:
        model = SuscripcionCliente
        fields = ['id', 'cliente', 'suscripcion', 'estado_pago', 'fecha_inicio', 'fecha_fin', 'fecha_pago']

    def to_representation(self, instance):
        """
        Personaliza la representación de la SuscripcionCliente.
        """
        # Obtenemos los datos de la suscripción y cliente
        representation = super().to_representation(instance)
        
        # Aquí puedes agregar datos personalizados si es necesario
        # Ejemplo, agregando un campo calculado (como los días restantes)
        if instance.fecha_fin:
            days_remaining = (instance.fecha_fin - instance.fecha_inicio).days
            representation['dias_restantes'] = days_remaining

        return representation
