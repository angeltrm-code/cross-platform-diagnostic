# Lanzador PowerShell para ejecutar el diagnóstico como administrador.
# Ejecutar este script con clic derecho → "Ejecutar con PowerShell"
# y, si es necesario, conceder permisos de ejecución de scripts.

param(
    [string]$PythonPath = "python"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $ScriptDir "..")
$MainPy  = Join-Path $RootDir "main.py"

Start-Process -FilePath $PythonPath -ArgumentList "`"$MainPy`"" -Verb RunAs
