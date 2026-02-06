# 📱 Guía Completa - Fábrica App (APK Android)

Esta guía te llevará paso a paso desde el código fuente hasta tu APK instalada en Android.

---

## 📋 Índice

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Método 1: Compilación Automática (GitHub Actions)](#método-1-compilación-automática-github-actions)
3. [Método 2: Compilación Local con Buildozer](#método-2-compilación-local-con-buildozer)
4. [Instalación en Android](#instalación-en-android)
5. [Uso de la Aplicación](#uso-de-la-aplicación)
6. [Solución de Problemas](#solución-de-problemas)

---

## 📁 Estructura del Proyecto

```
factory_apk/
├── app.py                 # Flask backend + API
├── models.py              # Modelos SQLAlchemy
├── buildozer.spec         # Configuración Buildozer
├── templates/
│   └── index.html         # SPA completa (UI)
├── static/                # Assets (CSS, fuentes)
├── database/              # SQLite (se crea automáticamente)
├── .github/
│   └── workflows/
│       └── main.yml       # CI/CD GitHub Actions
└── GUIA_COMPLETA.md       # Esta guía
```

---

## 🚀 Método 1: Compilación Automática (GitHub Actions) [RECOMENDADO]

Este método es el más fácil. GitHub compila el APK automáticamente en la nube.

### Paso 1: Crear Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Clic en el botón **"+"** (arriba a la derecha) → **"New repository"**
3. Nombre: `fabrica-app`
4. Descripción: `Sistema de gestión de fábrica para Android`
5. Selecciona **"Public"** (o Private si prefieres)
6. **NO** marques "Add a README file"
7. Clic en **"Create repository"**

### Paso 2: Subir el Código

```bash
# En tu computadora, navega a la carpeta del proyecto
cd factory_apk

# Inicializar git
git init

# Agregar todos los archivos
git add .

# Crear primer commit
git commit -m "Versión inicial - Fábrica App"

# Conectar con GitHub (reemplaza TU_USUARIO con tu nombre de usuario)
git remote add origin https://github.com/TU_USUARIO/fabrica-app.git

# Subir código
git push -u origin main
```

> **Nota:** Si usas Windows, descarga [Git for Windows](https://git-scm.com/download/win) primero.

### Paso 3: Activar GitHub Actions

1. En tu repositorio de GitHub, clic en la pestaña **"Actions"**
2. Si ves un mensaje sobre workflows, clic en **"I understand my workflows, go ahead and enable them"**
3. El workflow "Build Android APK" debería aparecer

### Paso 4: Ejecutar la Compilación

1. Clic en el workflow **"Build Android APK"**
2. Clic en el botón **"Run workflow"** (a la derecha)
3. Selecciona la rama `main`
4. Clic en **"Run workflow"**

La compilación tomará **15-30 minutos** la primera vez.

### Paso 5: Descargar el APK

1. Una vez terminada, clic en la ejecución más reciente
2. Espera a que aparezca ✅ verde
3. En la sección **"Artifacts"**, descarga **"Fábrica-App-APK"**
4. Descomprime el ZIP - dentro está tu archivo `.apk`

---

## 💻 Método 2: Compilación Local con Buildozer

Si prefieres compilar en tu propia computadora (Linux recomendado).

### Requisitos

- Linux (Ubuntu 20.04+ recomendado)
- Python 3.8+
- 10 GB de espacio libre
- Conexión a internet estable

### Paso 1: Instalar Dependencias del Sistema

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    python3-pip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake
```

### Paso 2: Instalar Buildozer

```bash
# Instalar buildozer y cython
pip3 install --user buildozer cython

# Agregar al PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Paso 3: Compilar el APK

```bash
# Navegar al proyecto
cd factory_apk

# Primera compilación (toma 30-60 minutos)
buildozer android debug

# El APK se generará en:
# bin/fabricaapp-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Recompilar (cambios posteriores)

```bash
# Si haces cambios, solo recompila:
buildozer android debug

# O para forzar rebuild completo:
buildozer android clean
buildozer android debug
```

---

## 📲 Instalación en Android

### Paso 1: Transferir el APK

1. Conecta tu tablet/teléfono a la computadora vía USB
2. Copia el archivo `.apk` al dispositivo
3. O envíalo por WhatsApp/Telegram/Email

### Paso 2: Habilitar Orígenes Desconocidos

En tu dispositivo Android:

1. Abre **Configuración**
2. Busca **"Seguridad"** o **"Aplicaciones"**
3. Activa **"Orígenes desconocidos"** o **"Instalar apps desconocidas"**
4. Busca tu navegador de archivos o app de mensajería
5. Activa el permiso para esa app

### Paso 3: Instalar

1. Abre el archivo APK desde tu gestor de archivos
2. Toca **"Instalar"**
3. Espera la instalación
4. Toca **"Abrir"**

---

## 🎮 Uso de la Aplicación

### Orientación Horizontal (Obligatoria)

La app **solo funciona en modo horizontal** (landscape).

- Si abres la app en vertical, verás un mensaje pidiendo que gires el dispositivo
- Gira tu tablet/teléfono 90 grados
- La app se mostrará automáticamente

### Navegación

```
┌─────────────────────────────────────────────────────────┐
│  [Sidebar]    │      [Contenido Principal]               │
│               │                                          │
│  🏠 Inicio    │   Dashboard con estadísticas             │
│  📦 Productos │   Cards de resumen financiero            │
│  ⚙️ Producción│   Alertas de stock bajo                  │
│  🛒 Ventas    │   Últimas ventas                         │
│  💰 Gastos    │                                          │
│  📄 Reportes  │   [Botones de acción rápida]            │
│               │                                          │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Trabajo Recomendado

1. **Configurar Productos**
   - Ve a "Productos"
   - Clic en "Nuevo"
   - Ingresa nombre y precios

2. **Registrar Gastos de Fábrica**
   - Ve a "Gastos"
   - Clic en "Nuevo Gasto"
   - Tipo: **Fábrica** (afecta costo unitario)
   - Ingresa monto y período

3. **Registrar Producción**
   - Ve a "Producción"
   - Clic en "Nueva"
   - Selecciona producto y cantidad
   - El costo unitario se calcula automáticamente

4. **Registrar Ventas**
   - Ve a "Ventas" o usa botón rápido
   - Selecciona producto y lote de producción
   - El sistema calcula la ganancia real

5. **Generar Reportes**
   - Ve a "Reportes"
   - Selecciona período
   - Clic en "Compartir"
   - Elige WhatsApp, Gmail, Drive, etc.

---

## 🔧 Solución de Problemas

### Error: "App not installed"

**Causa:** Ya existe una versión anterior con firma diferente

**Solución:**
```bash
# En Android:
Configuración > Aplicaciones > Fábrica App > Desinstalar
# Luego instala el nuevo APK
```

### Error: "Parse error"

**Causa:** APK corrupto o versión de Android incompatible

**Solución:**
- Verifica que tu Android sea 5.0+ (API 21+)
- Descarga el APK nuevamente

### La app se ve en vertical

**Causa:** El dispositivo está en modo portrait

**Solución:**
- Gira físicamente el dispositivo 90 grados
- Asegúrate de que la rotación automática esté activada

### Error al compilar en GitHub Actions

**Causa:** Límite de tiempo o caché corrupto

**Solución:**
1. Ve a Actions > Build Android APK
2. Clic en el workflow fallido
3. Clic en "Re-run jobs" > "Re-run all jobs"

### Error: "No module named 'flask'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install flask flask-sqlalchemy fpdf2
```

### El PDF no se comparte

**Causa:** Web Share API no soportado en el navegador

**Solución:**
- En Android nativo: funcionará correctamente
- En navegador desktop: se descargará el archivo
- Asegúrate de usar HTTPS en producción

---

## 📊 Fórmulas de Negocio Implementadas

### Costo Unitario Dinámico
```
Costo Unitario = Gastos de Fábrica del Mes ÷ Unidades Producidas
```

### Ganancia Real por Venta
```
Ganancia = (Precio × Cantidad - Descuento) - (Costo Unitario × Cantidad)
```

### Saldo Total Acumulado
```
Dinero Total = Σ Ventas - Σ Gastos (Fábrica + Personal)
```

---

## 🔄 Actualizar la App

### Para actualizar el código:

```bash
# Hacer cambios en los archivos
# Luego:
git add .
git commit -m "Nueva funcionalidad: X"
git push origin main
```

GitHub Actions compilará automáticamente el nuevo APK.

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs en GitHub Actions
2. Verifica que todos los archivos estén en su lugar
3. Asegúrate de que buildozer.spec esté configurado correctamente
4. Prueba compilar localmente para ver errores detallados

---

## 📝 Notas Importantes

- **Base de datos:** SQLite se almacena localmente en el dispositivo
- **Backup:** Los datos no se sincronizan en la nube automáticamente
- **Permisos:** La app necesita acceso a almacenamiento para compartir PDFs
- **Offline:** Funciona 100% sin internet

---

**¡Listo! Tu app de gestión de fábrica está completa.** 🎉
