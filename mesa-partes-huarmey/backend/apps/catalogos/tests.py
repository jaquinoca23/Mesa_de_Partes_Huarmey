from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import EstadoExpediente


class EstadoInicialTests(TestCase):
    def test_solo_puede_existir_un_estado_inicial(self):
        EstadoExpediente.objects.create(codigo='a', nombre='A', es_inicial=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EstadoExpediente.objects.create(codigo='b', nombre='B', es_inicial=True)

    def test_pueden_existir_varios_estados_no_iniciales(self):
        EstadoExpediente.objects.create(codigo='a', nombre='A')
        EstadoExpediente.objects.create(codigo='b', nombre='B')
        self.assertEqual(EstadoExpediente.objects.count(), 2)
