from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.catalogos.models import EstadoExpediente, TipoDocumental

from .models import Expediente, HistorialEstado, Solicitante, formatear_numero


class ExpedientesBaseTestCase(TestCase):
    """Datos mínimos de prueba (todos ficticios) que comparten las pruebas."""

    @classmethod
    def setUpTestData(cls):
        cls.tipo = TipoDocumental.objects.create(codigo='solicitud', nombre='Solicitud')
        cls.recibido = EstadoExpediente.objects.create(codigo='recibido', nombre='Recibido', es_inicial=True)
        cls.en_atencion = EstadoExpediente.objects.create(codigo='en-atencion', nombre='En atención')
        cls.persona = Solicitante.objects.create(
            tipo_persona='NATURAL',
            tipo_documento_identidad='DNI',
            numero_documento='00000001',
            nombres='Ana',
            apellidos='Ejemplo',
            email='ana@example.com',
        )

    def crear_expediente(self, asunto='Asunto de prueba'):
        return Expediente.objects.create(
            solicitante=self.persona,
            tipo_documental=self.tipo,
            estado_actual=self.recibido,
            asunto=asunto,
        )


class NumeracionTests(ExpedientesBaseTestCase):
    def test_el_servidor_asigna_numeros_consecutivos_sin_duplicados(self):
        anio = timezone.localtime(timezone.now()).year
        primero = self.crear_expediente('Uno')
        segundo = self.crear_expediente('Dos')
        self.assertEqual(primero.numero, formatear_numero(anio, 1))
        self.assertEqual(segundo.numero, formatear_numero(anio, 2))
        self.assertNotEqual(primero.numero, segundo.numero)

    def test_guardar_de_nuevo_no_cambia_el_numero(self):
        expediente = self.crear_expediente()
        numero = expediente.numero
        expediente.asunto = 'Asunto corregido'
        expediente.save()
        self.assertEqual(Expediente.objects.get(pk=expediente.pk).numero, numero)

    def test_identificadores_de_consulta_no_son_secuenciales(self):
        uno = self.crear_expediente('Uno')
        dos = self.crear_expediente('Dos')
        self.assertNotEqual(uno.uuid, dos.uuid)
        self.assertEqual(len(uno.codigo_verificacion), 8)


class SolicitanteTests(ExpedientesBaseTestCase):
    def test_no_se_duplica_el_mismo_documento_de_identidad(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Solicitante.objects.create(
                tipo_persona='NATURAL',
                tipo_documento_identidad='DNI',
                numero_documento='00000001',
                nombres='Otra',
                email='otra@example.com',
            )

    def test_persona_natural_exige_nombres(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Solicitante.objects.create(
                tipo_persona='NATURAL',
                tipo_documento_identidad='DNI',
                numero_documento='00000002',
                email='x@example.com',
            )

    def test_persona_juridica_exige_razon_social(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Solicitante.objects.create(
                tipo_persona='JURIDICA',
                tipo_documento_identidad='RUC',
                numero_documento='00000000001',
                email='x@example.com',
            )


class HistorialTests(ExpedientesBaseTestCase):
    def test_cambiar_estado_actualiza_y_registra_historial(self):
        expediente = self.crear_expediente()
        registro = expediente.cambiar_estado(self.en_atencion, observacion='Inicio de atención')
        expediente.refresh_from_db()
        self.assertEqual(expediente.estado_actual, self.en_atencion)
        self.assertEqual(registro.estado_anterior, self.recibido)
        self.assertEqual(expediente.historial.count(), 1)

    def test_no_se_puede_cambiar_al_mismo_estado(self):
        expediente = self.crear_expediente()
        with self.assertRaises(ValueError):
            expediente.cambiar_estado(self.recibido)

    def test_el_historial_no_se_puede_modificar_ni_eliminar(self):
        expediente = self.crear_expediente()
        registro = expediente.cambiar_estado(self.en_atencion)
        registro.observacion = 'Texto alterado'
        with self.assertRaises(ValidationError):
            registro.save()
        with self.assertRaises(ValidationError):
            registro.delete()
        self.assertEqual(HistorialEstado.objects.count(), 1)

    def test_no_se_puede_eliminar_un_expediente_con_historial(self):
        from django.db.models import ProtectedError

        expediente = self.crear_expediente()
        expediente.cambiar_estado(self.en_atencion)
        with self.assertRaises(ProtectedError):
            expediente.delete()
