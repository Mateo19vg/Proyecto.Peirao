# 🐟 Proyecto Peirao

## 📋 Requisitos previos

Antes de empezar, asegúrate de tener instalado en tu sistema:

- **Python** 3.10 o superior → [descargar](https://www.python.org/downloads/)
- **Node.js** 18 o superior (incluye npm) → [descargar](https://nodejs.org/)
- **Git** → [descargar](https://git-scm.com/)

Puedes verificar las versiones con:
```bash
python --version
node --version
npm --version
```

---

## 🚀 Guía de instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Mateo19vg/Proyecto.Peirao.git
cd Proyecto.Peirao
```

---

### 2. Configuración del Backend (Django)

#### 2.1 Ir a la carpeta del backend

```bash
cd backend
```

#### 2.2 Crear el entorno virtual

En **Linux/macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

En **Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Sabrás que el entorno está activo cuando veas `(venv)` al inicio de la línea de tu terminal.

#### 2.3 Instalar las dependencias de Python

```bash
pip install -r requirements.txt
```

#### 2.4 Aplicar las migraciones (crea la base de datos)

```bash
python manage.py migrate
```

Esto genera automáticamente el archivo `db.sqlite3` con todas las tablas necesarias (Especie, Spot, Captura).

#### 2.5 Cargar los datos iniciales

```bash
python manage.py loaddata initial_data.json
```

> El archivo `initial_data.json` se encuentra en `backend/` y contiene especies y spots de pesca preconfigurados.

#### 2.6 Iniciar el servidor backend

```bash
python manage.py runserver
```

El backend estará disponible en: **http://localhost:8000/**  
Puedes explorar la API en: **http://localhost:8000/api/**

---

### 3. Configuración del Frontend (React + Vite)

Abre una **nueva terminal** (mantén el backend corriendo) y desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en: **http://localhost:5173/**

