<#
Respaldo de la base de datos PostgreSQL y de los adjuntos privados (Windows / PowerShell).

Uso (desde la raíz del proyecto):
    powershell -ExecutionPolicy Bypass -File scripts\respaldo.ps1

Crea la carpeta backups\AAAAMMDD-HHMM\ con:
    base_datos.dump    (formato personalizado de pg_dump)
    adjuntos\          (copia de backend\storage_privado, si existe)

IMPORTANTE: los respaldos contienen DATOS PERSONALES. Guárdalos fuera del repositorio
(la carpeta backups\ ya está ignorada por Git), cifrados y con acceso restringido.
La contraseña se lee de backend\.env y NUNCA se imprime.
#>
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$envArchivo = Join-Path $raiz 'backend\.env'
if (-not (Test-Path $envArchivo)) { throw "No existe $envArchivo" }

# Lee las variables DB_* de .env
$config = @{}
Get-Content $envArchivo | ForEach-Object {
    if ($_ -match '^\s*(DB_[A-Z_]+)\s*=\s*(.*)\s*$') { $config[$matches[1]] = $matches[2] }
}
foreach ($clave in 'DB_NAME','DB_USER','DB_PASSWORD') { if (-not $config[$clave]) { throw "Falta $clave en backend\.env" } }
$servidor = if ($config['DB_HOST']) { $config['DB_HOST'] } else { 'localhost' }
$puerto = if ($config['DB_PORT']) { $config['DB_PORT'] } else { '5432' }

# Busca pg_dump
$pgDump = (Get-Command pg_dump -ErrorAction SilentlyContinue).Source
if (-not $pgDump) {
    $pgDump = Get-ChildItem 'C:\Program Files\PostgreSQL\*\bin\pg_dump.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $pgDump) { throw 'No se encontró pg_dump. Instala PostgreSQL o agrega su carpeta bin al PATH.' }

$destino = Join-Path $raiz ("backups\" + (Get-Date -Format 'yyyyMMdd-HHmm'))
New-Item -ItemType Directory -Force -Path $destino | Out-Null

$env:PGPASSWORD = $config['DB_PASSWORD']
try {
    & $pgDump -h $servidor -p $puerto -U $config['DB_USER'] -d $config['DB_NAME'] -F c -f (Join-Path $destino 'base_datos.dump')
    if ($LASTEXITCODE -ne 0) { throw "pg_dump terminó con error ($LASTEXITCODE)" }
} finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

$adjuntos = Join-Path $raiz 'backend\storage_privado'
if (Test-Path $adjuntos) { Copy-Item $adjuntos (Join-Path $destino 'adjuntos') -Recurse }

Write-Host "Respaldo creado en: $destino"
Write-Host 'Recuerda: contiene datos personales. Guárdalo cifrado y fuera del repositorio.'
