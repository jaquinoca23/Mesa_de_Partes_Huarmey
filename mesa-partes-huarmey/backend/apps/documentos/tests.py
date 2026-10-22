"""
Pruebas de los validadores de archivos.
No usan Django ni la base de datos, por lo que se pueden ejecutar solas:
    python -m unittest apps.documentos.tests
"""
import io
import unittest
import zipfile

from . import validadores

PERMITIDAS = validadores.normalizar_extensiones(['pdf', 'jpg', 'jpeg', 'png', 'docx'])
UN_MB = 1024 * 1024
PDF_VALIDO = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n'
PNG_VALIDO = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
JPG_VALIDO = b'\xff\xd8\xff\xe0' + b'\x00' * 20


def zip_con(nombres):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_:
        for nombre in nombres:
            zip_.writestr(nombre, 'x')
    return buffer.getvalue()


def revisar(nombre, contenido, permitidas=PERMITIDAS, maximo=UN_MB):
    return validadores.validar_archivo(nombre, len(contenido), lambda: contenido, permitidas, maximo)


class ArchivosValidosTests(unittest.TestCase):
    def test_pdf_valido(self):
        self.assertEqual(revisar('oficio.pdf', PDF_VALIDO), [])

    def test_imagenes_validas(self):
        self.assertEqual(revisar('foto.png', PNG_VALIDO), [])
        self.assertEqual(revisar('foto.JPG', JPG_VALIDO), [])

    def test_docx_valido(self):
        contenido = zip_con(['[Content_Types].xml', 'word/document.xml'])
        self.assertEqual(revisar('carta.docx', contenido), [])


class ArchivosRechazadosTests(unittest.TestCase):
    def test_ejecutable_renombrado_a_pdf(self):
        errores = revisar('informe.pdf', b'MZ\x90\x00\x03\x00\x00\x00')
        self.assertTrue(any('PDF válido' in e for e in errores))

    def test_texto_renombrado_a_png(self):
        self.assertTrue(revisar('foto.png', b'esto no es una imagen'))

    def test_extension_no_permitida(self):
        errores = revisar('programa.exe', b'MZ\x90\x00')
        self.assertTrue(any('no permitido' in e for e in errores))

    def test_extension_enganosa(self):
        errores = revisar('informe.exe.pdf', PDF_VALIDO)
        self.assertTrue(any('engañosa' in e for e in errores))

    def test_nombre_con_caracter_de_texto_invertido(self):
        errores = revisar('archivo‮gpj.pdf', PDF_VALIDO)
        self.assertTrue(any('control' in e for e in errores))

    def test_nombre_con_byte_nulo(self):
        self.assertTrue(revisar('informe.pdf\x00.exe', PDF_VALIDO))

    def test_nombre_sin_extension_o_terminado_en_punto(self):
        self.assertTrue(revisar('informe', PDF_VALIDO))
        self.assertTrue(revisar('informe.pdf.', PDF_VALIDO))

    def test_nombre_con_ruta(self):
        self.assertTrue(revisar('../secreto.pdf', PDF_VALIDO))

    def test_archivo_vacio(self):
        self.assertTrue(any('vacío' in e for e in revisar('a.pdf', b'')))

    def test_supera_el_tamano_y_no_se_lee_el_contenido(self):
        def leer():
            raise AssertionError('No debe leerse un archivo que supera el tamaño máximo.')

        errores = validadores.validar_archivo('a.pdf', 2 * UN_MB, leer, PERMITIDAS, UN_MB)
        self.assertTrue(any('tamaño máximo' in e for e in errores))

    def test_pdf_con_javascript(self):
        contenido = b'%PDF-1.4\n<< /S /JavaScript /JS (app.alert(1)) >>\n%%EOF'
        errores = revisar('a.pdf', contenido)
        self.assertTrue(any('código activo' in e for e in errores))

    def test_docx_con_macros(self):
        contenido = zip_con(['[Content_Types].xml', 'word/document.xml', 'word/vbaProject.bin'])
        self.assertTrue(any('macros' in e for e in revisar('a.docx', contenido)))

    def test_zip_que_no_es_docx(self):
        contenido = zip_con(['cualquier-cosa.txt'])
        self.assertTrue(revisar('a.docx', contenido))

    def test_extension_permitida_pero_no_verificable(self):
        permitidas = validadores.normalizar_extensiones(['txt'])
        self.assertTrue(revisar('nota.txt', b'hola', permitidas=permitidas))


class SanearNombreTests(unittest.TestCase):
    def test_quita_caracteres_invisibles_y_separadores(self):
        self.assertEqual(validadores.sanear_nombre('a‮b/c\\d.pdf'), 'ab_c_d.pdf')

    def test_nombre_vacio_se_reemplaza(self):
        self.assertEqual(validadores.sanear_nombre('\x00'), 'archivo')

    def test_se_recorta_al_maximo(self):
        self.assertEqual(len(validadores.sanear_nombre('a' * 400 + '.pdf')), validadores.MAX_LONGITUD_NOMBRE)


class ListaDeArchivosTests(unittest.TestCase):
    def test_demasiados_archivos(self):
        archivos = [(f'a{i}.pdf', len(PDF_VALIDO), lambda: PDF_VALIDO) for i in range(6)]
        errores = validadores.validar_lista(archivos, ['pdf'], UN_MB, 5)
        self.assertEqual(len(errores), 1)
        self.assertIn('máximo 5', errores[0])

    def test_el_mensaje_incluye_el_nombre_del_archivo(self):
        archivos = [('bueno.pdf', len(PDF_VALIDO), lambda: PDF_VALIDO), ('malo.exe', 4, lambda: b'MZ\x90\x00')]
        errores = validadores.validar_lista(archivos, ['pdf'], UN_MB, 5)
        self.assertEqual(len(errores), 1)
        self.assertTrue(errores[0].startswith('malo.exe:'))

    def test_lista_vacia_es_valida(self):
        self.assertEqual(validadores.validar_lista([], ['pdf'], UN_MB, 5), [])


if __name__ == '__main__':
    unittest.main()
