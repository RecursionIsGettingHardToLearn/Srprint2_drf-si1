# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pago,Usuario
from .utils import generar_pdf_comprobante
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

import logging
from .models import Usuario
import requests
import json
from django.conf import settings

# Configura el logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Pago)
def crear_comprobante_automatico(sender, instance, created, **kwargs):
    
    if created and not instance.comprobante:  # Solo si es nuevo y no tiene comprobante
        try:
            generar_pdf_comprobante(instance)
        except Exception as e:
            # Loggear error (opcional pero recomendado)
            print(f"Error generando comprobante para pago {instance.id}: {e}")
            # En producción, usa logging en vez de print

