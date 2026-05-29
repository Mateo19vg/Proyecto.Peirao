1. Clonar el repositorio
2. Abre una terminal y clona el proyecto en tu equipo:
git clone https://github.com/Mateo19vg/Proyecto.Peirao.git
cd Proyecto.Peirao
   Configuración del Backend (Django)
Puedes configurar el backend ejecutando los siguientes comandos:
Crear e iniciar el entorno virtual:
En Linux/macOS:
python3 -m venv venv
source venv/bin/activate
En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
Instalar las dependencias de Python:
Asegúrate de que estás en la carpeta raíz o donde se aloje el archivo requirements.txt:
pip install -r requirements.txt
Ejecutar las migraciones de la Base de Datos:
Crea la estructura de tablas de SQLite (modelos de Especie, Spot y Captura):
python manage.py migrate
Cargar los datos iniciales (Fixtures):
Para no empezar con la aplicación vacía, carga los datos de ejemplo preconfigurados (especies y spots de pesca):
python manage.py loaddata initial_data.json
Iniciar el servidor de desarrollo del backend:
python manage.py runserver
El backend estará disponible y escuchando peticiones en http://localhost:8000/.
Puedes visitar http://localhost:8000/api/ para inspeccionar la API REST a través del explorador interactivo.

  Configuración del Frontend (React + Vite)
Abre otra ventana de la terminal (manteniendo el servidor de Django corriendo) y dirígete a la carpeta del frontend para inicializarlo:
Instalar las dependencias de Node.js:
npm install
Iniciar el servidor de desarrollo de Vite:
npm run dev
El frontend compilará y se levantará en http://localhost:5173/.
