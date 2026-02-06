# 📱 Fábrica App - Sistema de Gestión para Android

Aplicación de gestión de fábrica diseñada específicamente para convertirse en APK Android, funcionando en **modo horizontal (landscape)** como una aplicación de escritorio.

![Landscape Mode](https://img.shields.io/badge/Orientation-Landscape-blue)
![Platform](https://img.shields.io/badge/Platform-Android-green)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

---

## ✨ Características

- 🌙 **Tema Oscuro** profesional con Tailwind CSS
- 📊 **Dashboard** con estadísticas en tiempo real
- 📦 **Gestión de Productos** con stock y precios
- ⚙️ **Control de Producción** con costos unitarios dinámicos
- 🛒 **Registro de Ventas** vinculadas a lotes de producción
- 💰 **Gestión de Gastos** (Fábrica vs Personal)
- 📄 **Reportes PDF** con Web Share API para compartir
- 📱 **Diseño Responsive** optimizado para tablets

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    ANDROID DEVICE                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │  WebView (Landscape)                            │    │
│  │  ┌─────────────────────────────────────────┐   │    │
│  │  │  Flask Server (localhost:5000)          │   │    │
│  │  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ │   │    │
│  │  │  │  API    │ │   PDF    │ │  SQLite  │ │   │    │
│  │  │  │ Routes  │ │ Generator│ │  Database│ │   │    │
│  │  │  └─────────┘ └──────────┘ └──────────┘ │   │    │
│  │  └─────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Inicio Rápido

### Opción 1: Descargar APK Pre-compilado

1. Ve a la pestaña **"Actions"** de este repositorio
2. Selecciona el último workflow exitoso ✅
3. Descarga el artifact **"Fábrica-App-APK"**
4. Instala en tu dispositivo Android

### Opción 2: Compilar Localmente

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/fabrica-app.git
cd fabrica-app

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python app.py

# Compilar APK (requiere Linux)
buildozer android debug
```

---

## 📋 Estructura del Proyecto

```
factory_apk/
├── app.py              # Flask backend + API REST
├── models.py           # Modelos SQLAlchemy
├── buildozer.spec      # Configuración Buildozer
├── requirements.txt    # Dependencias Python
├── templates/
│   └── index.html      # SPA completa (Single Page Application)
├── static/             # Assets estáticos
├── database/           # SQLite (auto-generado)
├── .github/
│   └── workflows/
│       └── main.yml    # CI/CD GitHub Actions
└── GUIA_COMPLETA.md    # Guía detallada
```

---

## 💡 Lógica de Negocio

### Costo Unitario Dinámico

```python
Costo Unitario = Gastos de Fábrica del Mes ÷ Unidades Producidas
```

**Ejemplo:**
- Gastos de Fábrica (Feb 2026): Gs. 800.000
- Unidades Producidas: 200
- **Costo Unitario: Gs. 4.000**

### Ganancia Real por Venta

```python
Ganancia = Ingreso Total - Costo Total
         = (Precio × Cantidad - Descuento) - (Costo Unitario × Cantidad)
```

### Saldo Total Acumulado

```python
Dinero Total = Σ Todas las Ventas - Σ Todos los Gastos
```

---

## 🔌 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página principal (SPA) |
| GET | `/api/dashboard` | Estadísticas del dashboard |
| GET | `/api/productos` | Listar productos |
| POST | `/api/productos` | Crear producto |
| PUT | `/api/productos/<id>` | Actualizar producto |
| DELETE | `/api/productos/<id>` | Eliminar producto |
| GET | `/api/produccion` | Listar producción |
| POST | `/api/produccion` | Crear producción |
| GET | `/api/ventas` | Listar ventas |
| POST | `/api/ventas` | Crear venta |
| GET | `/api/gastos` | Listar gastos |
| POST | `/api/gastos` | Crear gasto |
| GET | `/api/reportes/pdf` | Generar PDF |

---

## 📱 Web Share API

La aplicación utiliza la **Web Share API** para compartir PDFs:

```javascript
// Compartir PDF nativamente en Android
const file = new File([pdfBlob], 'reporte.pdf', { type: 'application/pdf' });

await navigator.share({
    files: [file],
    title: 'Reporte de Fábrica',
    text: 'Reporte mensual'
});
// Abre: WhatsApp, Gmail, Drive, Telegram, etc.
```

---

## 🎨 Diseño UI/UX

### Modo Horizontal Forzado

```css
@media (orientation: portrait) {
    #app-container { display: none !important; }
    #orientation-warning { display: flex !important; }
}
```

### Botones Táctiles Optimizados

- Tamaño mínimo: **48x48px**
- Espaciado amplio para evitar toques accidentales
- Feedback visual al presionar

### Tema Oscuro

```css
--bg-primary: #0a0f1a;
--bg-secondary: #0f172a;
--bg-tertiary: #1e293b;
--accent-blue: #3b82f6;
--accent-green: #22c55e;
--accent-red: #ef4444;
```

---

## 🔧 Configuración Buildozer

El archivo `buildozer.spec` configura:

- **Orientación:** Landscape (horizontal)
- **WebView:** Flask corre en localhost:5000
- **Permisos:** Internet, Almacenamiento
- **Arquitecturas:** ARM64, ARMv7

```ini
orientation = landscape
android.webview = True
android.webview_url = http://localhost:5000
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE
```

---

## 🔄 CI/CD GitHub Actions

El workflow `.github/workflows/main.yml`:

1. ✅ Instala Python y dependencias
2. ✅ Configura Android SDK/NDK
3. ✅ Ejecuta Buildozer
4. ✅ Sube APK como artifact
5. ✅ Crea release automático

**Tiempo de compilación:** 15-30 minutos

---

## 📝 Formato de Moneda

Todos los montos se muestran en **Guaraníes (PYG)**:

```python
def format_guaranies(valor):
    return f"Gs. {valor:,.0f}".replace(",", ".")

# Ejemplos:
# 1500000 -> Gs. 1.500.000
# 50000   -> Gs. 50.000
```

---

## 🐛 Depuración

### Ver logs en Android

```bash
# Conectar dispositivo vía USB
adb devices

# Ver logs
adb logcat | grep python
```

### Modo desarrollo

```bash
# Ejecutar Flask localmente
python app.py

# Abrir en navegador
http://localhost:5000
```

---

## 📦 Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| Flask | 3.0.0 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM para SQLite |
| fpdf2 | 2.7.6 | Generación de PDFs |
| buildozer | latest | Compilación APK |

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

---

## 📄 Licencia

Este proyecto es de código abierto. Puedes usarlo, modificarlo y distribuirlo libremente.

---

## 🙏 Créditos

- **Framework:** Flask
- **UI:** Tailwind CSS
- **PDF:** fpdf2
- **Build:** Buildozer
- **Icons:** Font Awesome

---

**Desarrollado con ❤️ para fábricas de Paraguay**

¿Preguntas? Revisa la [Guía Completa](GUIA_COMPLETA.md)
