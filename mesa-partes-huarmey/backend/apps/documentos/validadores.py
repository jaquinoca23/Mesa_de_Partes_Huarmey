"""
Validación segura de archivos adjuntos.

Este módulo NO depende de Django: recibe datos simples y devuelve listas de mensajes de
error en español (lista vacía = archivo aceptable). Así se puede probar de forma aislada.

Qué comprueba (los tipos permitidos y los límites son configurables en settings/.env):
  1. Nombre: sin caracteres de control (incluidos los trucos de texto invertido), sin
     separadores de ruta, sin punto o espacio al final y sin "extensiones engañosas"
     (por ejemplo informe.exe.pdf).
  2. Extensión: solo las permitidas.
  3. Tamaño: nunca vacío ni mayor al máximo (se revisa ANTES de leer el contenido).
  4. Contenido real: los primeros bytes (la "firma" del formato) deben corresponder a la
     extensión declarada. Un .exe renombrado a .pdf se rechaza. También se rechazan los PDF
     con JavaScript o acciones de ejecución y los documentos de Office con macros.

LIMITACIONES (pendiente para la ETAPA 9): esto reduce el riesgo, pero no reemplaza a un
antivirus ni a un análisis profundo de cada formato.
"""
import io
import re
import unicodedata
import zipfile

# Extensiones de programas, scripts y documentos con macros. Si aparecen "en medio" del nombre
# (informe.exe.pdf) se rechaza el archivo: es un truco típico para engañar al usuario.
EXTENSIONES_PELIGROSAS = frozenset({
    'exe', 'com', 'bat', 'cmd', 'scr', 'pif', 'msi', 'msp', 'dll', 'sys', 'cpl', 'lnk',
    'jar', 'js', 'jse', 'vbs', 'vbe', 'wsf', 'wsh', 'ps1', 'psm1', 'sh', 'bash', 'py',
    'rb', 'pl', 'php', 'phtml', 'asp', 'aspx', 'jsp', 'cgi', 'html', 'htm', 'xhtml', 'svg',
    'hta', 'reg', 'iso', 'img', 'apk', 'app', 'deb', 'rpm', 'dmg', 'inf', 'scf', 'url',
    'gadget', 'docm', 'xlsm', 'pptm', 'dotm', 'xltm',
})

# Formatos cuyo contenido sabemos verificar. Una extensión permitida que no esté aquí se
# rechaza (no se puede comprobar que sea lo que dice ser).
EXTENSIONES_VERIFICABLES = frozenset({'pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx'})

MAX_LONGITUD_NOMBRE = 150
MAX_ENTRADAS_ZIP = 2000
MAX_BYTES_DESCOMPRIMIDOS = 100 * 1024 * 1024  # 100 MB (protección contra "bombas zip")

FIRMA_PDF = b'%PDF-'
FIRMA_JPEG = b'\xff\xd8\xff'
FIRMA_PNG = b'\x89PNG\r\n\x1a\n'

# Marcas de PDF con código activo. (Los PDF que las ocultan en flujos comprimidos no se
# detectan: por eso hará falta un antivirus en la ETAPA 9.)
PATRON_PDF_ACTIVO = re.compile(rb'/(?:JavaScript|JS|Launch)(?![A-Za-z0-9])')


def normalizar_extensiones(extensiones):
    """Convierte ['PDF', '.jpg'] en {'pdf', 'jpg'}."""
    return frozenset(str(e).strip().lower().lstrip('.') for e in extensiones if str(e).strip())


def nombre_para_mostrar(nombre):
    """Versión segura del nombre para mostrarlo en un mensaje (sin caracteres invisibles)."""
    limpio = ''.join(c for c in str(nombre) if not unicodedata.category(c).startswith('C'))
    return limpio[:60] or 'archivo'


def sanear_nombre(nombre):
    """Nombre limpio para guardarlo como dato: sin caracteres invisibles ni separadores de ruta."""
    limpio = ''.join(c for c in str(nombre) if not unicodedata.category(c).startswith('C'))
    limpio = limpio.replace('/', '_').replace('\\', '_').strip()
    return (limpio or 'archivo')[:MAX_LONGITUD_NOMBRE]


def validar_nombre(nombre):
    """Devuelve la lista de problemas del nombre del archivo (vacía si está bien)."""
    nombre = '' if nombre is None else str(nombre)
    if not nombre.strip():
        return ['El archivo no tiene nombre.']
    if len(nombre) > MAX_LONGITUD_NOMBRE:
        return [f'El nombre es demasiado largo (máximo {MAX_LONGITUD_NOMBRE} caracteres).']
    # Cc = caracteres de control (como el byte nulo); Cf = de formato (como el que invierte el texto).
    if any(unicodedata.category(c) in ('Cc', 'Cf') for c in nombre):
        return ['El nombre contiene caracteres de control no permitidos.']
    if '/' in nombre or '\\' in nombre or nombre in ('.', '..'):
        return ['El nombre contiene separadores de ruta no permitidos.']
    if nombre != nombre.strip() or nombre.endswith('.'):
        return ['El nombre no puede terminar en punto ni en espacio.']
    partes = nombre.lower().split('.')
    if len(partes) < 2:
        return ['El archivo no tiene extensión.']
    if partes[0] == '':
        return ['El nombre del archivo no es válido.']
    for intermedia in partes[1:-1]:
        if intermedia.strip() in EXTENSIONES_PELIGROSAS:
            return [f'El nombre tiene una extensión engañosa (".{intermedia.strip()}").']
    return []


def _validar_ooxml(datos, carpeta):
    """Documentos de Office modernos (.docx, .xlsx): son archivos ZIP con una estructura conocida."""
    if not zipfile.is_zipfile(io.BytesIO(datos)):
        return ['El contenido no corresponde a un documento de Office válido.']
    try:
        with zipfile.ZipFile(io.BytesIO(datos)) as zip_:
            entradas = zip_.infolist()
            if len(entradas) > MAX_ENTRADAS_ZIP:
                return ['El documento tiene una estructura interna sospechosa.']
            if sum(e.file_size for e in entradas) > MAX_BYTES_DESCOMPRIMIDOS:
                return ['El documento es demasiado grande una vez descomprimido.']
            nombres = [e.filename for e in entradas]
    except zipfile.BadZipFile:
        return ['El documento está dañado o no es válido.']
    if '[Content_Types].xml' not in nombres or not any(n.startswith(carpeta) for n in nombres):
        return ['El contenido no corresponde a un documento de Office válido.']
    if any(n.lower().endswith('vbaproject.bin') for n in nombres):
        return ['El documento contiene macros, que no están permitidas.']
    return []


def validar_contenido(extension, datos):
    """Comprueba que los bytes del archivo correspondan a la extensión declarada."""
    if extension == 'pdf':
        if not datos.startswith(FIRMA_PDF):
            return ['El contenido no es un PDF válido.']
        if PATRON_PDF_ACTIVO.search(datos):
            return ['El PDF contiene código activo (JavaScript o ejecución de programas), que no está permitido.']
        return []
    if extension in ('jpg', 'jpeg'):
        return [] if datos.startswith(FIRMA_JPEG) else ['El contenido no es una imagen JPG válida.']
    if extension == 'png':
        return [] if datos.startswith(FIRMA_PNG) else ['El contenido no es una imagen PNG válida.']
    if extension == 'docx':
        return _validar_ooxml(datos, 'word/')
    if extension == 'xlsx':
        return _validar_ooxml(datos, 'xl/')
    return ['No es posible verificar el contenido de este tipo de archivo.']


def validar_archivo(nombre, tamano, leer, extensiones_permitidas, tamano_max_bytes):
    """
    Valida UN archivo. Devuelve una lista de mensajes (vacía = aceptable).

    nombre: nombre original; tamano: bytes; leer: función SIN argumentos que devuelve todo el
    contenido (solo se llama si el nombre, la extensión y el tamaño ya pasaron la revisión).
    extensiones_permitidas: conjunto normalizado (ver normalizar_extensiones).
    """
    errores = validar_nombre(nombre)
    if errores:
        return errores
    extension = nombre.rsplit('.', 1)[-1].lower()
    if extension not in extensiones_permitidas:
        permitidas = ', '.join(sorted(e.upper() for e in extensiones_permitidas))
        return [f'Tipo de archivo no permitido. Permitidos: {permitidas}.']
    if tamano <= 0:
        return ['El archivo está vacío.']
    if tamano > tamano_max_bytes:
        return [f'Supera el tamaño máximo de {tamano_max_bytes / (1024 * 1024):g} MB.']
    return validar_contenido(extension, leer())


def validar_lista(archivos, extensiones_permitidas, tamano_max_bytes, max_archivos):
    """
    Valida varios archivos. 'archivos' es una lista de tuplas (nombre, tamano, leer).
    Devuelve una lista de mensajes, cada uno con el nombre del archivo afectado.
    """
    permitidas = normalizar_extensiones(extensiones_permitidas)
    if len(archivos) > max_archivos:
        return [f'Puedes adjuntar como máximo {max_archivos} archivos (enviaste {len(archivos)}).']
    errores = []
    for nombre, tamano, leer in archivos:
        for mensaje in validar_archivo(nombre, tamano, leer, permitidas, tamano_max_bytes):
            errores.append(f'{nombre_para_mostrar(nombre)}: {mensaje}')
    return errores
