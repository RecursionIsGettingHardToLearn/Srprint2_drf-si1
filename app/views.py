from datetime import timedelta
from rest_framework.exceptions import NotFound

from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Group, Permission as AuthPermission
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets,status
from  django.utils import timezone
from .models import Bitacora,SuscripcionCliente
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import MyTokenPairSerializer,LogoutSerializer,SuscripcionSerializer
class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class = MyTokenPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # ← ESTE es el usuario autenticado

        # IP (X-Forwarded-For si hay proxy; si no, REMOTE_ADDR)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None

        # User-Agent como "device" (o None si vacío)
        device = request.META.get('HTTP_USER_AGENT') or None

        # Registrar login en bitácora
        Bitacora.objects.create(
            usuario=user,
            login=timezone.now(),
            ip=ip,
            device=device
        )
        print('el usuario ingreso al perfil',)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
#vistas
"""
{
  "refresh": "...",
  "password": "..."
}

"""
class LogoutView(APIView):
    """
    Endpoint de **logout**.
    Requiere `{"refresh": "<jwt-refresh-token>"}` en el cuerpo (JSON).
    Blacklistea el refresh token mediante SimpleJWT y registra el logout en Bitacora si corresponde.
    Retorna 204 en caso de éxito.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]  # fuerza a intentar parsear JSON

    def post(self, request):
        # --- DEBUG: cuerpo crudo + datos parseados + headers ---
        raw = request.body.decode("utf-8", errors="replace")
        headers = {
            k: v for k, v in request.META.items()
            if k.startswith("HTTP_") or k in ("CONTENT_TYPE", "CONTENT_LENGTH")
        }

        #logger.info("=== RAW BODY === %s", raw)
        #logger.info("=== PARSED DATA === %s", request.data)
        #logger.info("=== HEADERS === %s", headers)
    
        # invalidamos el refresh token
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ——————— Registro de logout ———————
        bit = Bitacora.objects.filter(
            usuario=request.user,
            logout__isnull=True
        ).last()
        if bit:
            print('no se esta cerrando seccion ')
            bit.logout = timezone.now()
            bit.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
import django_filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .mixin import BitacoraLoggerMixin
from .models import (
    Usuario, Rol, Administrativo, Instructor, Nutricionista,
    Cliente, Antecedentes, Seguimiento, Rutina, Ejercicio, DetalleRutina,
    Disciplina, Sala, Horario, Reserva, Suscripcion, Promocion, Pago, 
 Bitacora, DetalleBitacora
)

from .serializers import (
    UsuarioSerializer, RolSerializer, AdministrativoSerializer,
    InstructorSerializer, NutricionistaSerializer, ClienteSerializer, 
    AntecedentesSerializer, SeguimientoSerializer, RutinaSerializer, 
    EjercicioSerializer, DetalleRutinaSerializer, DisciplinaSerializer,
    SalaSerializer, HorarioSerializer, ReservaSerializer, SuscripcionSerializer,
    PromocionSerializer, PagoSerializer, BitacoraSerializer,
    DetalleBitacoraSerializer, MyTokenPairSerializer, LogoutSerializer, 
    UsuarioMeSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
User = get_user_model()

# ViewSets para modelos base


# Filtro personalizado para el rol del usuario
class UsuarioFilter(django_filters.FilterSet):
    rol_nombre = django_filters.CharFilter(field_name='rol__nombre', lookup_expr='iexact')

    class Meta:
        model = Usuario
        fields = ['rol_nombre']

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()  # Este es el queryset por defecto
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsuarioFilter  # Asigna el filtro a la vista

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener información del usuario autenticado
        """
        serializer = UsuarioMeSerializer(request.user)
        return Response(serializer.data)
 
class RolViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]



class AdministrativoViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Administrativo.objects.all()
    serializer_class = AdministrativoSerializer
    permission_classes = [IsAuthenticated]

class InstructorViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [IsAuthenticated]

class NutricionistaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Nutricionista.objects.all()
    serializer_class = NutricionistaSerializer
    permission_classes = [IsAuthenticated]

class ClienteViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def antecedentes(self, request, pk=None):
        """
        Obtener todos los antecedentes de un cliente
        """
        cliente = self.get_object()
        antecedentes = cliente.antecedentes.all()
        serializer = AntecedentesSerializer(antecedentes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def seguimientos(self, request, pk=None):
        """
        Obtener todos los seguimientos de un cliente
        """
        cliente = self.get_object()
        seguimientos = cliente.seguimientos.all()
        serializer = SeguimientoSerializer(seguimientos, many=True)
        return Response(serializer.data)

class AntecedentesViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Antecedentes.objects.all()
    serializer_class = AntecedentesSerializer
    permission_classes = [IsAuthenticated]

class SeguimientoViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def rutinas(self, request, pk=None):
        """
        Obtener todas las rutinas de un seguimiento
        """
        seguimiento = self.get_object()
        rutinas = seguimiento.rutinas.all()
        serializer = RutinaSerializer(rutinas, many=True)
        return Response(serializer.data)

class RutinaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtener todos los detalles de una rutina
        """
        rutina = self.get_object()
        detalles = rutina.detalles.all()
        serializer = DetalleRutinaSerializer(detalles, many=True)
        return Response(serializer.data)

class EjercicioViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer
    permission_classes = [IsAuthenticated]

class DetalleRutinaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = DetalleRutina.objects.all()
    serializer_class = DetalleRutinaSerializer
    permission_classes = [IsAuthenticated]

class DisciplinaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Disciplina.objects.all()
    serializer_class = DisciplinaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def horarios(self, request, pk=None):
        """
        Obtener todos los horarios de una disciplina
        """
        disciplina = self.get_object()
        horarios = disciplina.horarios.all()
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)

class SalaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def horarios(self, request, pk=None):
        """
        Obtener todos los horarios de una sala
        """
        sala = self.get_object()
        horarios = sala.horarios.all()
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)

class HorarioViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """
        Obtener todas las reservas de un horario
        """
        horario = self.get_object()
        reservas = horario.reservas.all()
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        """
        Verificar disponibilidad de cupos en un horario
        """
        horario = self.get_object()
        reservas_count = horario.reservas.filter(estado='Confirmada').count()
        cupos_disponibles = horario.cupo - reservas_count
        return Response({
            'cupo_total': horario.cupo,
            'reservas_confirmadas': reservas_count,
            'cupos_disponibles': cupos_disponibles,
            'disponible': cupos_disponibles > 0
        })

class ReservaViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """
        Confirmar una reserva
        """
        reserva = self.get_object()
        reserva.estado = 'Confirmada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancelar una reserva
        """
        reserva = self.get_object()
        reserva.estado = 'Cancelada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

class SuscripcionViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Suscripcion.objects.all()
    serializer_class = SuscripcionSerializer
    permission_classes = [IsAuthenticated]
    # GET: Obtener la lista de suscripciones
    def list(self, request):
        """
        Obtiene una lista de todas las suscripciones.
        """
        return super().list(request)

    # POST: Crear una nueva suscripción
    def create(self, request):
        """
        Crea una nueva suscripción con los datos proporcionados.
        """
        return super().create(request)

    # GET: Obtener los detalles de una suscripción específica
    def retrieve(self, request, pk=None):
        """
        Recupera los detalles de una suscripción por su ID.
        """
        return super().retrieve(request, pk=pk)

    # PUT: Actualizar una suscripción existente
    def update(self, request, pk=None):
        """
        Actualiza los datos de una suscripción específica.
        """
        return super().update(request, pk=pk)

    # PATCH: Actualización parcial de una suscripción
    def partial_update(self, request, pk=None):
        """
        Actualiza parcialmente los datos de una suscripción específica.
        """
        return super().partial_update(request, pk=pk)

    # DELETE: Eliminar una suscripción
    def destroy(self, request, pk=None):
        """
        Elimina una suscripción específica.
        """
        return super().destroy(request, pk=pk)
    
from rest_framework import viewsets
from .models import SuscripcionCliente
from .serializers import SuscripcionClienteSerializer
from rest_framework.permissions import IsAuthenticated

class SuscripcionClienteViewSet(viewsets.ModelViewSet):
    queryset = SuscripcionCliente.objects.all()
    serializer_class = SuscripcionClienteSerializer
    permission_classes = [IsAuthenticated]

    # Esta acción personaliza cómo se devuelven las suscripciones de un cliente específico
    @action(detail=True, methods=['get'])
    def suscripciones_cliente(self, request, pk=None):
        """
        Obtener todas las suscripciones de un cliente específico
        """
        cliente = self.get_object()
        suscripciones = cliente.suscripciones.all()  # Relación de suscripciones del cliente
        serializer = SuscripcionClienteSerializer(suscripciones, many=True)
        return Response(serializer.data)
    def list(self, request):
        """
        Obtiene una lista de todas las suscripciones de los clientes.
        """
        return super().list(request)

    # POST: Crear una nueva suscripción para un cliente
    def create(self, request):
        """
        Crea una nueva relación de suscripción entre un cliente y una suscripción.
        """
        return super().create(request)

    # GET: Obtener los detalles de una suscripción cliente
    def retrieve(self, request, pk=None):
        """
        Recupera los detalles de una relación de suscripción cliente.
        """
        return super().retrieve(request, pk=pk)

    # PUT: Actualizar una relación de suscripción cliente
    def update(self, request, pk=None):
        """
        Actualiza los datos de una relación de suscripción cliente específica.
        """
        return super().update(request, pk=pk)

    # PATCH: Actualización parcial de una relación de suscripción cliente
    def partial_update(self, request, pk=None):
        """
        Actualiza parcialmente los datos de una relación de suscripción cliente.
        """
        return super().partial_update(request, pk=pk)

    # DELETE: Eliminar una relación de suscripción cliente
    def destroy(self, request, pk=None):
        """
        Elimina una relación de suscripción cliente específica.
        """
        return super().destroy(request, pk=pk)

    # GET: Obtener todas las suscripciones de un cliente específico
    @action(detail=True, methods=['get'])
    def suscripciones_cliente(self, request, pk=None):
        """
        Obtener todas las suscripciones de un cliente específico.
        """
        cliente = self.get_object()
        suscripciones = cliente.suscripciones.all()  # Relación de suscripciones del cliente
        serializer = SuscripcionClienteSerializer(suscripciones, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='mis-suscripciones')
    def mis_suscripciones(self, request):

        try:
            cliente = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            raise NotFound(detail="No se encontró un cliente asociado a este usuario.")
    
        suscripciones = SuscripcionCliente.objects.filter(cliente=cliente)
        serializer = SuscripcionClienteSerializer(suscripciones, many=True)
        return Response(serializer.data)


class PromocionViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
    permission_classes = [IsAuthenticated]

    # GET: Obtener la lista de promociones
    def list(self, request):
        """
        Obtiene una lista de todas las promociones.
        """
        return super().list(request)

    # POST: Crear una nueva promoción
    def create(self, request):
        """
        Crea una nueva promoción con los datos proporcionados.
        """
        return super().create(request)

    # GET: Obtener los detalles de una promoción específica
    def retrieve(self, request, pk=None):
        """
        Recupera los detalles de una promoción específica.
        """
        return super().retrieve(request, pk=pk)

    # PUT: Actualizar una promoción existente
    def update(self, request, pk=None):
        """
        Actualiza los datos de una promoción específica.
        """
        return super().update(request, pk=pk)

    # PATCH: Actualización parcial de una promoción
    def partial_update(self, request, pk=None):
        """
        Actualiza parcialmente los datos de una promoción.
        """
        return super().partial_update(request, pk=pk)

    # DELETE: Eliminar una promoción
    def destroy(self, request, pk=None):
        """
        Elimina una promoción específica.
        """
        return super().destroy(request, pk=pk)

    # GET: Obtener todas las promociones activas
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Obtiene todas las promociones activas (en el rango de fechas actuales).
        """
        hoy = timezone.now().date()
        promociones = Promocion.objects.filter(
            estado=True,
            fecha_ini__lte=hoy,
            fecha_fin__gte=hoy
        )
        serializer = self.get_serializer(promociones, many=True)
        return Response(serializer.data)
class PagoViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """
        Obtener el comprobante de un pago
        """
        pago = self.get_object()
        try:
            comprobante = pago.comprobante
            serializer = ComprobanteSerializer(comprobante)
            return Response(serializer.data)
        except Comprobante.DoesNotExist:
            return Response(
                {'error': 'Este pago no tiene comprobante asociado'},
                status=status.HTTP_404_NOT_FOUND
            )



class BitacoraViewSet(BitacoraLoggerMixin,viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Bitácora (auditoría)
    """
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtener todos los detalles de una bitácora
        """
        bitacora = self.get_object()
        detalles = bitacora.detallebitacoras.all()
        serializer = DetalleBitacoraSerializer(detalles, many=True)
        return Response(serializer.data)

class DetalleBitacoraViewSet(BitacoraLoggerMixin,viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para DetalleBitacora (auditoría)
    """
    queryset = DetalleBitacora.objects.all()
    serializer_class = DetalleBitacoraSerializer
    permission_classes = [IsAuthenticated]

# Vista personalizada para login con JWT
class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class = MyTokenPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # ← ESTE es el usuario autenticado

        # IP (X-Forwarded-For si hay proxy; si no, REMOTE_ADDR)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None

        # User-Agent como "device" (o None si vacío)
        device = request.META.get('HTTP_USER_AGENT') or None

        # Registrar login en bitácora
        Bitacora.objects.create(
            usuario=user,
            login=timezone.now(),
            ip=ip,
            device=device
        )
        print('el usuario ingreso al perfil',)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


#vistas
"""
{
  "refresh": "...",
  "password": "..."
}

"""
class LogoutView(APIView):
    """
    Endpoint de **logout**.
    Requiere `{"refresh": "<jwt-refresh-token>"}` en el cuerpo (JSON).
    Blacklistea el refresh token mediante SimpleJWT y registra el logout en Bitacora si corresponde.
    Retorna 204 en caso de éxito.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]  # fuerza a intentar parsear JSON

    def post(self, request):
        # --- DEBUG: cuerpo crudo + datos parseados + headers ---
        raw = request.body.decode("utf-8", errors="replace")
        headers = {
            k: v for k, v in request.META.items()
            if k.startswith("HTTP_") or k in ("CONTENT_TYPE", "CONTENT_LENGTH")
        }

        #logger.info("=== RAW BODY === %s", raw)
        #logger.info("=== PARSED DATA === %s", request.data)
        #logger.info("=== HEADERS === %s", headers)
    
        # invalidamos el refresh token
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ——————— Registro de logout ———————
        bit = Bitacora.objects.filter(
            usuario=request.user,
            logout__isnull=True
        ).last()
        if bit:
            print('no se esta cerrando seccion ')
            bit.logout = timezone.now()
            bit.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
import logging
from rest_framework.response import Response
from rest_framework import status

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import stripe
import logging

logger = logging.getLogger(__name__)

import stripe
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import Suscripcion, Cliente, SuscripcionCliente, Pago
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

import stripe
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import Suscripcion, Cliente, SuscripcionCliente, Pago
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
import stripe
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.error("No se recibió firma de Stripe")
        return HttpResponse(status=400)

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Payload inválido: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Firma inválida: {str(e)}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Obtener metadata
        metadata = session.get('metadata', {})
        tipo_objeto = metadata.get('tipo_objeto')
        objeto_id = metadata.get('objeto_id')
        usuario_id = metadata.get('usuario_id')

        logger.info(f"Webhook recibido - Tipo: {tipo_objeto}, Objeto ID: {objeto_id}, Usuario ID: {usuario_id}")

        if not all([tipo_objeto, objeto_id, usuario_id]):
            logger.error(f"Metadata incompleta: {metadata}")
            return HttpResponse(status=400)

        try:
            usuario = Usuario.objects.get(id=usuario_id)
            monto = session['amount_total'] / 100  # convertir de centavos a unidades

            referencia = session.get('payment_intent') or session.get('id')

            logger.info(f"Procesando pago - Usuario: {usuario.email}, Monto: {monto}, Referencia: {referencia}")

            # Evitar duplicados de pago
            existing_pago = Pago.objects.filter(
                referencia=referencia, 
                usuario=usuario
            ).first()

            if existing_pago:
                logger.info(f"Pago duplicado detectado con referencia: {referencia}")
                return HttpResponse(status=200)

            # Obtener el objeto relacionado ANTES de crear el pago
            objeto_relacionado = None
            content_type = None

            if tipo_objeto == 'suscripcion':
                objeto_relacionado = Suscripcion.objects.get(id=objeto_id)
                content_type = ContentType.objects.get_for_model(Suscripcion)
            elif tipo_objeto == 'promocion':
                objeto_relacionado = Promocion.objects.get(id=objeto_id)
                content_type = ContentType.objects.get_for_model(Promocion)

            # Crear el Pago con el content_type y object_id
            pago = Pago.objects.create(
                usuario=usuario,
                tipo_pago=tipo_objeto,
                monto=monto,
                metodo_pago='tarjeta',
                referencia=referencia,
                fecha_pago=timezone.now(),
                content_type=content_type,
                object_id=objeto_id
            )

            logger.info(f"Pago creado exitosamente: ID {pago.id}")

            # Lógica para suscripciones
            if tipo_objeto == 'suscripcion':
                try:
                    objeto_relacionado = Suscripcion.objects.get(id=objeto_id)
                    cliente = Cliente.objects.get(usuario=usuario)

                    # Calcular fechas según el tipo de suscripción
                    fecha_inicio = timezone.now().date()
                    
                    if objeto_relacionado.tipo == 'Mensual':
                        fecha_fin = fecha_inicio + timedelta(days=30)
                    elif objeto_relacionado.tipo == 'Anual':
                        fecha_fin = fecha_inicio + timedelta(days=365)
                    else:
                        logger.error(f"Tipo de suscripción no válido: {objeto_relacionado.tipo}")
                        return HttpResponse(status=400)

                    # Crear o actualizar la suscripción del cliente
                    suscripcion_cliente, created = SuscripcionCliente.objects.get_or_create(
                        cliente=cliente, 
                        suscripcion=objeto_relacionado,
                        defaults={ 
                            'fecha_inicio': fecha_inicio,
                            'fecha_fin': fecha_fin,
                            'fecha_pago': timezone.now().date(),
                            'estado_pago': True
                        }
                    )

                    # Si ya existía, actualizar los valores (renovación)
                    if not created:
                        suscripcion_cliente.estado_pago = True
                        suscripcion_cliente.fecha_pago = timezone.now().date()
                        suscripcion_cliente.fecha_inicio = fecha_inicio
                        suscripcion_cliente.fecha_fin = fecha_fin
                        suscripcion_cliente.save()

                    # Relacionar la suscripción al cliente
                    cliente.suscripcion_actual = objeto_relacionado
                    cliente.save()

                    logger.info(f"Suscripción {objeto_id} {'creada' if created else 'actualizada'} para el cliente {usuario_id}")

                except Suscripcion.DoesNotExist:
                    logger.error(f"Suscripción no encontrada con ID: {objeto_id}")
                    return HttpResponse(status=404)
                except Cliente.DoesNotExist:
                    logger.error(f"Cliente no encontrado para el usuario ID: {usuario_id}")
                    return HttpResponse(status=404)

            # Lógica para promociones
            elif tipo_objeto == 'promocion':
                try:
                    objeto_relacionado.estado = True
                    objeto_relacionado.save()
                    logger.info(f"Promoción {objeto_id} activada")
                except Exception as e:
                    logger.error(f"Error al activar promoción: {str(e)}")
                    return HttpResponse(status=500)

        except Usuario.DoesNotExist:
            logger.error(f"Usuario no encontrado: {usuario_id}")
            return HttpResponse(status=404)
        except (Suscripcion.DoesNotExist, Promocion.DoesNotExist) as e:
            logger.error(f"Objeto no encontrado: {tipo_objeto} con ID {objeto_id}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Error inesperado en webhook: {str(e)}", exc_info=True)
            return HttpResponse(status=500)

    return HttpResponse(status=200)

# Backend: PagoViewSet o SuscripcionClienteViewSet (dependiendo de cómo estés manejando la creación)
from datetime import timedelta

class PagoViewSet(BitacoraLoggerMixin, viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('usuario').all()  # Optimized queryset
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def crear_sesion_stripe(self, request):
        """
        Crea una sesión de Stripe Checkout para pagar una suscripción o promoción.
        """
        tipo_objeto = request.data.get('tipo_objeto')  # 'suscripcion' o 'promocion'
        objeto_id = request.data.get('objeto_id')
        success_url = request.data.get('success_url')
        cancel_url = request.data.get('cancel_url')

        if not all([tipo_objeto, objeto_id, success_url, cancel_url]):
            return Response({"error": "Faltan parámetros."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificamos si el cliente ya tiene una suscripción activa
            cliente = Cliente.objects.get(usuario=request.user)

            # Comprobamos si el cliente ya tiene una suscripción activa
            suscripcion_activa = SuscripcionCliente.objects.filter(cliente=cliente, estado_pago=True).first()

            if suscripcion_activa:
                # Si ya tiene una suscripción activa, no permitimos crear una nueva
                return Response({"error": "Usted ya tiene una suscripción activa."}, status=status.HTTP_400_BAD_REQUEST)

            # Código existente para crear la sesión de Stripe
            if tipo_objeto == 'suscripcion':
                objeto = Suscripcion.objects.get(id=objeto_id)
                nombre_producto = f"Suscripción {objeto.nombre}"
                monto = int(objeto.precio * 100)  # Stripe usa centavos
            elif tipo_objeto == 'promocion':
                objeto = Promocion.objects.get(id=objeto_id)
                nombre_producto = f"Promoción {objeto.nombre}"
                monto = int(objeto.descuento * 100)  # Descuento en centavos, puedes adaptarlo si es monto fijo
            else:
                return Response({"error": "Tipo de objeto no soportado."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear sesión de Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',  # o tu moneda local
                        'product_data': {
                            'name': nombre_producto,
                        },
                        'unit_amount': monto,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'tipo_objeto': tipo_objeto,
                    'objeto_id': str(objeto_id),
                    'usuario_id': str(request.user.id),
                }
            )

            return Response({
                'id': session.id,
                'url': session.url
            })

        except (Suscripcion.DoesNotExist, Promocion.DoesNotExist):
            return Response({"error": "Objeto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





