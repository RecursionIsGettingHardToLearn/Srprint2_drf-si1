# app/rol/management/commands/populate_roles.py

from django.core.management.base import BaseCommand
from app.models import Rol

class Command(BaseCommand):
    help = 'Pobla la base de datos con los roles predeterminados'

    def handle(self, *args, **kwargs):
        roles = ['Administrador', 'Nutricionista', 'Cliente', 'Instructor']
        
        for rol in roles:
            # Crear un rol si no existe
            if not Rol.objects.filter(nombre=rol).exists():
                Rol.objects.create(nombre=rol)
        
        self.stdout.write(self.style.SUCCESS('Roles creados exitosamente'))
