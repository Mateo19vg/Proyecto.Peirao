# Proyecto.Peirao
⚙️ Instalación y arranque
El proyecto tiene dos partes independientes que hay que arrancar en dos terminales distintas.
Terminal 1 — Backend (Django)
bash# 1. Entrar en la carpeta del backend
cd backend

# 2. Crear el entorno virtual
python3 -m venv .venv

# 3. Activar el entorno virtual
#    En Linux / macOS:
source .venv/bin/activate
#    En Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 4. Instalar dependencias Python
pip install -r requirements.txt

# 5. Crear las tablas en la base de datos
python manage.py migrate

# 6. (Opcional) Cargar datos de ejemplo — spots y especies de Galicia
python manage.py loaddata api/fixtures/initial_data.json

# 7. (Opcional) Crear superusuario para acceder al panel de administración
python manage.py createsuperuser

# 8. Arrancar el servidor de desarrollo
python manage.py runserver
✅ El backend queda disponible en: http://127.0.0.1:8000
✅ Panel de administración: http://127.0.0.1:8000/admin

Terminal 2 — Frontend (React + Vite)
bash# 1. Entrar en la carpeta del frontend
cd frontend

# 2. Instalar dependencias Node
npm install

# 3. Arrancar el servidor de desarrollo
npm run dev
✅ La aplicación queda disponible en: http://localhost:5173

El proxy de Vite redirige automáticamente todas las llamadas a /api/* al backend en el puerto 8000, por lo que no hace falta configurar nada más.
