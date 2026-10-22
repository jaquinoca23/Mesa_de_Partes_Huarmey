"""Pruebas de la ETAPA 6: sesión, CSRF, roles, permisos en el servidor y gestión de usuarios."""
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.auditoria.models import RegistroAuditoria
from apps.organizacion.models import Area

from .models import Usuario

CLAVE = 'Clave-Segura-9182!'


def cliente_con_csrf():
    """Cliente que EXIGE token CSRF, como un navegador real."""
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.get('/api/auth/csrf/')
    return cliente


def cabecera(cliente):
    return {'HTTP_X_CSRFTOKEN': cliente.cookies['csrftoken'].value}


class BaseUsuarios(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_roles_demo', '--password', CLAVE, verbosity=0)

    def setUp(self):
        cache.clear()

    def entrar(self, username):
        cliente = cliente_con_csrf()
        r = cliente.post('/api/auth/login/', {'username': username, 'password': CLAVE}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 200, r.content)
        return cliente


class SesionTests(BaseUsuarios):
    def test_login_correcto_devuelve_roles_y_permisos(self):
        cliente = self.entrar('mesa.demo')
        datos = cliente.get('/api/auth/me/').json()['usuario']
        self.assertEqual(datos['roles'], ['Mesa de partes'])
        self.assertIn('expedientes.view_expediente', datos['permisos'])
        self.assertNotIn('password', str(datos))
        self.assertTrue(RegistroAuditoria.objects.filter(accion='LOGIN').exists())

    def test_login_sin_csrf_se_rechaza(self):
        cliente = APIClient(enforce_csrf_checks=True)
        r = cliente.post('/api/auth/login/', {'username': 'mesa.demo', 'password': CLAVE}, format='json')
        self.assertEqual(r.status_code, 403)

    def test_login_incorrecto_mensaje_generico_y_auditoria(self):
        cliente = cliente_con_csrf()
        a = cliente.post('/api/auth/login/', {'username': 'mesa.demo', 'password': 'mala'}, format='json', **cabecera(cliente))
        b = cliente.post('/api/auth/login/', {'username': 'no.existe', 'password': 'mala'}, format='json', **cabecera(cliente))
        self.assertEqual(a.status_code, 400)
        self.assertEqual(a.json(), b.json())
        self.assertEqual(RegistroAuditoria.objects.filter(accion='LOGIN_FALLIDO').count(), 2)

    def test_usuario_inactivo_no_entra(self):
        Usuario.objects.filter(username='mesa.demo').update(is_active=False)
        cliente = cliente_con_csrf()
        r = cliente.post('/api/auth/login/', {'username': 'mesa.demo', 'password': CLAVE}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 400)

    def test_limite_de_intentos_de_login(self):
        cliente = cliente_con_csrf()
        codigos = [
            cliente.post('/api/auth/login/', {'username': 'x', 'password': 'y'}, format='json', **cabecera(cliente)).status_code
            for _ in range(12)
        ]
        self.assertIn(429, codigos)

    def test_me_sin_sesion_se_rechaza(self):
        self.assertIn(APIClient().get('/api/auth/me/').status_code, (401, 403))

    def test_logout_cierra_la_sesion(self):
        cliente = self.entrar('mesa.demo')
        self.assertEqual(cliente.post('/api/auth/logout/', **cabecera(cliente)).status_code, 200)
        self.assertIn(cliente.get('/api/auth/me/').status_code, (401, 403))

    def test_logout_sin_csrf_se_rechaza(self):
        cliente = self.entrar('mesa.demo')
        self.assertEqual(APIClient.post(cliente, '/api/auth/logout/').status_code, 403)


class PermisosPanelTests(BaseUsuarios):
    URLS = ['/api/panel/usuarios/', '/api/panel/areas/', '/api/panel/tipos-documentales/', '/api/panel/estados/', '/api/panel/roles/']

    def test_anonimo_no_accede_a_nada(self):
        for url in self.URLS:
            self.assertIn(APIClient().get(url).status_code, (401, 403), url)

    def test_sin_permiso_no_accede(self):
        cliente = self.entrar('area1.demo')  # funcionario de área: sin permisos de administración
        for url in self.URLS:
            self.assertEqual(cliente.get(url).status_code, 403, url)

    def test_administrador_accede(self):
        cliente = self.entrar('admin.demo')
        for url in self.URLS:
            self.assertEqual(cliente.get(url).status_code, 200, url)

    def test_roles_solo_lectura_no_pueden_modificar(self):
        # Sin permiso "add", un POST se rechaza aunque pueda ver.
        grupo = Group.objects.get(name='Consulta y reportes')
        from django.contrib.auth.models import Permission
        grupo.permissions.add(Permission.objects.get(codename='view_area'))
        cliente = self.entrar('auditor.demo')
        self.assertEqual(cliente.get('/api/panel/areas/').status_code, 200)
        r = cliente.post('/api/panel/areas/', {'nombre': 'X', 'tipo': 'OFICINA'}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 403)

    def test_no_se_puede_eliminar(self):
        cliente = self.entrar('admin.demo')
        area = Area.objects.create(nombre='Temporal', tipo='OFICINA')
        r = cliente.delete(f'/api/panel/areas/{area.pk}/', **cabecera(cliente))
        self.assertEqual(r.status_code, 405)
        self.assertTrue(Area.objects.filter(pk=area.pk).exists())

    def test_modificar_sin_csrf_se_rechaza(self):
        cliente = self.entrar('admin.demo')
        r = APIClient.post(cliente, '/api/panel/areas/', {'nombre': 'X', 'tipo': 'OFICINA'}, format='json')
        self.assertEqual(r.status_code, 403)


class GestionUsuariosTests(BaseUsuarios):
    def crear(self, cliente, **cambios):
        datos = {
            'username': 'nuevo.demo', 'first_name': 'Nuevo', 'last_name': 'Demo', 'email': 'nuevo@example.com',
            'password': CLAVE, 'roles': ['Mesa de partes'], 'is_active': True,
        }
        datos.update(cambios)
        return cliente.post('/api/panel/usuarios/', datos, format='json', **cabecera(cliente))

    def test_crear_usuario_con_rol_y_sin_exponer_la_clave(self):
        cliente = self.entrar('admin.demo')
        r = self.crear(cliente)
        self.assertEqual(r.status_code, 201, r.content)
        self.assertNotIn('password', r.json())
        usuario = Usuario.objects.get(username='nuevo.demo')
        self.assertTrue(usuario.check_password(CLAVE))
        self.assertNotEqual(usuario.password, CLAVE)  # guardada con hash
        self.assertEqual([g.name for g in usuario.groups.all()], ['Mesa de partes'])
        self.assertTrue(RegistroAuditoria.objects.filter(accion='USUARIO_CREADO').exists())

    def test_contrasena_debil_se_rechaza(self):
        cliente = self.entrar('admin.demo')
        self.assertEqual(self.crear(cliente, password='12345678').status_code, 400)

    def test_contrasena_obligatoria_al_crear(self):
        cliente = self.entrar('admin.demo')
        self.assertEqual(self.crear(cliente, password='').status_code, 400)

    def test_rol_inexistente_se_rechaza(self):
        cliente = self.entrar('admin.demo')
        self.assertEqual(self.crear(cliente, roles=['Superjefe']).status_code, 400)

    def test_no_puede_desactivarse_a_si_mismo(self):
        cliente = self.entrar('admin.demo')
        yo = Usuario.objects.get(username='admin.demo')
        r = cliente.patch(f'/api/panel/usuarios/{yo.pk}/', {'is_active': False}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 400)

    def test_editar_sin_clave_no_la_cambia(self):
        cliente = self.entrar('admin.demo')
        objetivo = Usuario.objects.get(username='mesa.demo')
        r = cliente.patch(f'/api/panel/usuarios/{objetivo.pk}/', {'cargo': 'Otro cargo'}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 200)
        objetivo.refresh_from_db()
        self.assertEqual(objetivo.cargo, 'Otro cargo')
        self.assertTrue(objetivo.check_password(CLAVE))

    def test_no_administrador_no_puede_dar_rol_administrador_ni_ver_administradores(self):
        grupo = Group.objects.get(name='Mesa de partes')
        from django.contrib.auth.models import Permission
        grupo.permissions.add(*Permission.objects.filter(content_type__app_label='usuarios', codename__endswith='usuario'))
        cliente = self.entrar('mesa.demo')
        self.assertEqual(self.crear(cliente, roles=['Administrador']).status_code, 400)
        nombres = [u['username'] for u in cliente.get('/api/panel/usuarios/').json()]
        self.assertNotIn('admin.demo', nombres)
        admin = Usuario.objects.get(username='admin.demo')
        r = cliente.patch(f'/api/panel/usuarios/{admin.pk}/', {'password': CLAVE}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 404)

    def test_superusuario_oculto_para_administrador(self):
        Usuario.objects.create_superuser('super.demo', 'super@example.com', CLAVE)
        cliente = self.entrar('admin.demo')
        nombres = [u['username'] for u in cliente.get('/api/panel/usuarios/').json()]
        self.assertNotIn('super.demo', nombres)


class AreasYCatalogosTests(BaseUsuarios):
    def test_area_no_puede_depender_de_su_dependencia(self):
        cliente = self.entrar('admin.demo')
        a = Area.objects.create(nombre='A', tipo='OFICINA')
        b = Area.objects.create(nombre='B', tipo='OFICINA', padre=a)
        r = cliente.patch(f'/api/panel/areas/{a.pk}/', {'padre': b.pk}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 400)

    def test_un_solo_estado_inicial(self):
        from apps.catalogos.models import EstadoExpediente
        EstadoExpediente.objects.create(codigo='recibido', nombre='Recibido', es_inicial=True)
        cliente = self.entrar('admin.demo')
        r = cliente.post('/api/panel/estados/', {'codigo': 'otro', 'nombre': 'Otro', 'es_inicial': True}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 400)

    def test_crear_tipo_documental_deja_auditoria(self):
        cliente = self.entrar('admin.demo')
        r = cliente.post('/api/panel/tipos-documentales/', {'codigo': 'nuevo', 'nombre': 'Nuevo tipo'}, format='json', **cabecera(cliente))
        self.assertEqual(r.status_code, 201, r.content)
        self.assertTrue(RegistroAuditoria.objects.filter(accion='CATALOGO_CREADO').exists())

    def test_auditoria_no_se_puede_modificar(self):
        from django.core.exceptions import ValidationError
        registro = RegistroAuditoria.objects.create(accion='LOGIN')
        registro.detalle = 'cambio'
        with self.assertRaises(ValidationError):
            registro.save()
        with self.assertRaises(ValidationError):
            registro.delete()

    def test_roles_demo_se_puede_repetir(self):
        call_command('crear_roles_demo', verbosity=0)
        self.assertEqual(Usuario.objects.filter(username__endswith='.demo').count(), 5)
