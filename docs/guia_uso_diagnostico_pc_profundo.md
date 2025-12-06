# Guía de uso – Diagnóstico PC Profundo

Esta guía está pensada para que una persona **no técnica** pueda usar la herramienta y enviar el informe a alguien que le ayude.

---

## 1. Preparación (normalmente la hace el técnico)

### 1.1. Descomprimir el proyecto

1. Descomprime el `.zip` del proyecto en una carpeta, por ejemplo:
   - Windows: `C:\Diagnostico_pc_profundo\`
   - Linux: `~/Diagnostico_pc_profundo/`
2. Dentro verás archivos como:
   - `main.py`
   - carpeta `src/`
   - carpeta `launchers/`
   - `requirements.txt`

### 1.2. Instalar Python y dependencias (lo hace el técnico)

#### Windows

1. Instalar **Python 3** (si no está instalado) desde la web oficial, marcando la casilla **"Add Python to PATH"**.
2. Abrir **CMD** o **PowerShell** en la carpeta del proyecto.
3. Ejecutar:

```bash
pip install -r requirements.txt
```

#### Linux (incluido KDE Neon)

1. Comprobar que existen Python 3 y pip3:

```bash
python3 --version
pip3 --version
```

2. En la carpeta del proyecto:

```bash
pip3 install --user -r requirements.txt
```

3. Dar permisos al lanzador:

```bash
chmod +x launchers/run_linux.sh
```

A partir de aquí, el usuario ya no necesita saber nada de pip ni Python. Solo usará los ejecutables preparados.

---

## 2. Uso en Windows (usuario no técnico)

### 2.1. Ejecutar el diagnóstico

Tienes dos formas de usarlo. Elige la que te resulte más cómoda.

#### Opción A: doble clic en `run_windows.bat` (modo normal)

1. Abre la carpeta del proyecto.
2. Entra en la carpeta `launchers`.
3. Haz doble clic en `run_windows.bat`.
4. Se abrirá una ventana negra (consola) y verás mensajes como:

```text
[ 14%] Detectando sistema operativo...
[ 28%] Comprobando privilegios...
[ 42%] Recopilando información profunda del sistema...
...
Diagnóstico completado.
Informe generado en: C:\Users\TU_USUARIO\Desktop\diagnostico_pc_profundo_...
```

> Si solo quieres revisar el estado del PC y no tienes permisos de administrador, esta opción te vale.

#### Opción B: ejecutarlo como administrador (recomendado)

1. Abre la carpeta `launchers`.
2. Haz **clic derecho** sobre `run_windows_admin.ps1`.
3. Elige **"Ejecutar con PowerShell"**.
4. Acepta los avisos de seguridad si aparecen.
5. Se abrirá una ventana con los mismos mensajes de progreso.

> En este modo el programa puede leer más información interna del sistema y el informe será más completo.

---

### 2.2. Dónde se guarda el informe

Al terminar, verás algo como:

```text
Informe generado en: C:\Users\TU_USUARIO\Desktop\diagnostico_pc_profundo_2025...
```

Esto significa que el informe está en tu **Escritorio**, con un nombre parecido a:

```text
diagnostico_pc_profundo_20251206_153045.txt
```

Pasos:

1. Ve al Escritorio.
2. Busca el archivo `diagnostico_pc_profundo_... .txt`.
3. Ábrelo con el Bloc de notas.
4. Si tienes un técnico de confianza, puedes **enviarle ese archivo** por correo o por donde prefieras.

---

### 2.3. Cómo leer el informe si no eres técnico

El archivo tiene dos partes importantes:

1. `=== RESUMEN PARA USUARIO NO TÉCNICO ===`
2. `=== DETALLE TÉCNICO ===`

Como usuario no técnico, céntrate en la primera.

#### Claves del resumen

- Verás algo como:

```text
Estado general de tu equipo: OK
```

Puede ser:

- `OK` → Todo razonablemente bien.
- `AVISO` → Hay cosas a vigilar (no es pánico, pero conviene revisar).
- `CRITICO` → Hay problemas importantes que conviene mirar pronto.

- Luego aparece "Estado por áreas", por ejemplo:

```text
[OK]      Memoria: OK
[AVISO]   Disco: AVISO
[OK]      Registros de eventos: OK
```

Fíjate especialmente en:

- **Memoria** → si sale AVISO/CRÍTICO, el equipo puede ir lento por falta de RAM.
- **Disco** → si sale AVISO/CRÍTICO, el disco puede estar casi lleno o tener problemas.
- **Registros de eventos** → si hay muchos errores, el sistema se ha quejado bastante.

También verás un texto sobre los **últimos 7 días**, por ejemplo:

```text
En la última semana se han registrado eventos relevantes. Errores: 12, avisos: 8. Las áreas más sospechosas son: disco, drivers.
```

Eso indica en qué parte del equipo pueden estar los problemas:

- Disco
- Red
- Memoria
- Drivers / tarjeta gráfica, etc.

Al final hay unas recomendaciones en lenguaje normal:

- Si todo está **OK** → tranquilidad.
- Si hay **AVISO** → coméntalo con tu técnico cuando puedas.
- Si hay **CRITICO** → mejor que alguien lo mire pronto.

---

## 3. Uso en Linux / KDE Neon (usuario no técnico)

### 3.1. Ejecutar el diagnóstico

1. Abre una **Terminal**.
2. Entra en la carpeta del proyecto, por ejemplo:

```bash
cd ~/Diagnostico_pc_profundo
```

3. Ejecuta el lanzador:

```bash
./launchers/run_linux.sh
```

Si te dice "Permiso denegado", primero:

```bash
chmod +x launchers/run_linux.sh
./launchers/run_linux.sh
```

Verás mensajes de progreso como en Windows:

```text
[ 14%] Detectando sistema operativo...
[ 28%] Comprobando privilegios...
...
Informe generado en: /home/tu_usuario/Escritorio/diagnostico_pc_profundo_...
```

> Si quieres que vea más información de sistema (logs que requieren root), puedes lanzarlo con `sudo`:
>
> ```bash
> sudo ./launchers/run_linux.sh
> ```

---

### 3.2. Dónde se guarda el informe

Se guarda en tu **Escritorio**. Según el idioma del sistema puede ser:

- `~/Escritorio`
- `~/Desktop`

El programa detecta automáticamente la carpeta correcta si existe.

---

### 3.3. Cómo leerlo

1. Busca el archivo `diagnostico_pc_profundo_YYYYMMDD_HHMMSS.txt` en el Escritorio.
2. Ábrelo con tu editor de texto favorito (Kate, KWrite, etc.).
3. Igual que en Windows, céntrate en la parte:

```text
=== RESUMEN PARA USUARIO NO TÉCNICO ===
```

4. Mira:
   - "Estado general de tu equipo: ..."
   - Estado de Memoria / Disco / Registros.
   - El resumen de lo ocurrido en los últimos 7 días.

5. Si ves **AVISO** o **CRÍTICO** y notas problemas (lentitud, cuelgues, reinicios), envía ese archivo a la persona que te ayuda con el PC.

---

## 4. Resumen ultra corto para el usuario final

1. Ejecuta el archivo preparado:
   - En Windows: doble clic en `run_windows.bat` o `run_windows_admin.ps1`.
   - En Linux: `./launchers/run_linux.sh` (o `sudo ./launchers/run_linux.sh`).
2. Espera a que la ventana termine y ponga algo como:

   ```text
   Diagnóstico completado.
   Informe generado en: ...
   ```

3. Ve a tu Escritorio y abre el archivo `diagnostico_pc_profundo_....txt`.
4. Lee la parte "RESUMEN PARA USUARIO NO TÉCNICO" para ver si todo está OK, AVISO o CRÍTICO.
5. Si ves AVISO o CRÍTICO, envía ese archivo a tu técnico para que lo revise en detalle.

