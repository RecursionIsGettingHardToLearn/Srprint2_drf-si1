from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MyTokenObtainPairView, LogoutView,
    UsuarioViewSet, RolViewSet, AdministrativoViewSet,
    InstructorViewSet, NutricionistaViewSet, ClienteViewSet,
    AntecedentesViewSet, SeguimientoViewSet, RutinaViewSet,
    EjercicioViewSet, DetalleRutinaViewSet, DisciplinaViewSet,
    SalaViewSet, HorarioViewSet, ReservaViewSet,
    SuscripcionViewSet, PromocionViewSet, PagoViewSet,
     BitacoraViewSet, DetalleBitacoraViewSet,SuscripcionClienteViewSet
)

# Crear el router y registrar todos los ViewSets
router = DefaultRouter()

# Registrar ViewSets de usuarios y roles
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')

# Registrar ViewSets de tipos de usuario
router.register(r'administrativos', AdministrativoViewSet, basename='administrativo')
router.register(r'instructores', InstructorViewSet, basename='instructor')
router.register(r'nutricionistas', NutricionistaViewSet, basename='nutricionista')
router.register(r'clientes', ClienteViewSet, basename='cliente')

# Registrar ViewSets de seguimiento médico y nutricional
router.register(r'antecedentes', AntecedentesViewSet, basename='antecedente')
router.register(r'seguimientos', SeguimientoViewSet, basename='seguimiento')

# Registrar ViewSets de rutinas y ejercicios
router.register(r'rutinas', RutinaViewSet, basename='rutina')
router.register(r'ejercicios', EjercicioViewSet, basename='ejercicio')
router.register(r'detalle-rutinas', DetalleRutinaViewSet, basename='detalle-rutina')

# Registrar ViewSets de disciplinas y salas
router.register(r'disciplinas', DisciplinaViewSet, basename='disciplina')
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'reservas', ReservaViewSet, basename='reserva')

# Registrar ViewSets de suscripciones y pagos
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')
router.register(r'promociones', PromocionViewSet, basename='promocion')
router.register(r'pagos', PagoViewSet, basename='pago')

# Registrar ViewSets de auditoría (solo lectura)
router.register(r'bitacoras', BitacoraViewSet, basename='bitacora')
router.register(r'detalle-bitacoras', DetalleBitacoraViewSet, basename='detalle-bitacora')

# Registrar el ViewSet de SuscripcionCliente
router.register(r'suscripciones-clientes', SuscripcionClienteViewSet, basename='suscripcion-cliente')
from .views import stripe_webhook
urlpatterns = [
    # Rutas de autenticación
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]