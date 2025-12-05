# Buscador Semántico (Proyecto)

Este repositorio contiene una aplicación de búsqueda semántica para películas:

- Backend: API en Python (FastAPI) que carga un modelo de embeddings, un índice FAISS y metadata en español.
- Frontend: SPA en React (Vite) que consume la API para mostrar resultados, pósters y trailers.

Este README explica cómo replicar el entorno localmente, regenerar los artefactos (metadata, embeddings y FAISS) y ejecutar la aplicación tanto en desarrollo como en producción.

**Contenido**

- **Requisitos**: versiones recomendadas y alternativas (conda) para Windows.
- **Instalación backend**: crear entorno virtual, instalar dependencias, configuración de claves API.
- **Generar/actualizar datos**: cómo crear `metadata_es.csv`, `embeddings_es.npy` y `faiss_index_es.bin` (scripts incluidos).
- **Ejecutar backend**: comandos para arrancar la API.
- **Instalación frontend**: instalar dependencias y ejecutar Vite.
- **Despliegue / Build**: pasos mínimos para producción.
- **Solución de problemas**: errores frecuentes y recomendaciones.

--

**Estructura relevante del proyecto**

- `backend/` : código del servidor (API, loaders, scripts de preprocesado) y la carpeta `backend/data/` con artefactos.
- `frontend/` : aplicación React con `package.json` y scripts Vite.
- `build_index.py`, `README.md` (este archivo) en la raíz.

--

**Requisitos (sistemas Windows - PowerShell)**

- Python 3.10 o 3.11 (recomendado). Alternativa: usar Anaconda/Miniconda si hay problemas con paquetes binarios (FAISS, torch).
- Node.js >= 16 (recomendado Node 18+). `npm` incluido con Node.
- Herramientas: `git`, `curl`/`wget` opcional.

Nota: algunos paquetes como `faiss-cpu` y `sentence-transformers`/`torch` pueden requerir instalación vía conda en Windows para evitar errores binarios. Se incluyen instrucciones alternativas más abajo.

--

**Instalación y ejecución: Backend**

1) Crear y activar un entorno virtual (PowerShell):

```powershell
# (desde la raíz del repositorio)
python -m venv .venv
# Si PowerShell bloquea scripts, ejecutar (una vez) como administrador o usuario:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Activar el virtualenv
.\.venv\Scripts\Activate.ps1
```

2) Actualizar `pip` e instalar dependencias:

```powershell
pip install --upgrade pip
pip install -r backend/requirements.txt
```

3) Configurar claves API necesarias:

- Pósters (OMDB): en `backend/api.py` hay una variable `OMDB_KEY = "cfd4f5c2"`. Sustituye ese valor por tu clave OMDb (recomendado).
- TMDB (proveedores): en `backend/preprocess_dataset.py` hay `TMDB_API_KEY = "026cab6..."` — reemplázala por tu clave TMDB si vas a ejecutar el preprocesado para obtener proveedores reales.

Ejemplo: editar `backend/api.py` y reemplazar la línea:

```python
OMDB_KEY = "cfd4f5c2"  # tu key OMDB
```

por:

```python
OMDB_KEY = "TU_OMDB_KEY_AQUI"
```

4) Ejecutar la API (desde la raíz del repo):

```powershell
# desde la raíz
uvicorn backend.api:app --reload --port 8000
```

La API quedará disponible en `http://localhost:8000`.

--

**Generar o regenerar datos (metadata, embeddings, FAISS)**

El proyecto incluye artefactos ya generados en `backend/data/` (`metadata_es.csv`, `embeddings_es.npy`, `faiss_index_es.bin`). Si quieres regenerarlos desde cero (por ejemplo tras modificar el CSV o actualizar proveedores), sigue estos pasos.

1) Requisitos previos:
- Asegúrate de tener las claves TMDB configuradas en `backend/preprocess_dataset.py` (variable `TMDB_API_KEY`).
- Estás usando el virtualenv y las dependencias instaladas.

2) Ejecutar el script de preprocesado (genera `metadata_es.csv`, `embeddings_es.npy`, `faiss_index_es.bin`):

```powershell
cd backend
python preprocess_dataset.py
```

El script realizará llamadas a TMDB para obtener proveedores por país y luego generará los embeddings y el índice FAISS. El resultado se guardará en `backend/data/`.

Nota: la generación de embeddings puede tardar bastante (según tu CPU/GPU y tamaño del dataset). Si tienes problemas con `faiss-cpu` en Windows, considera usar WSL o conda (ver sección de solución de problemas).

--

**Instalación y ejecución: Frontend (React + Vite)**

1) Instalar dependencias:

```powershell
cd frontend
npm install
```

2) Ejecutar en modo desarrollo:

```powershell
npm run dev
```

Por defecto Vite sirve la app en `http://localhost:5173` (o el puerto libre que asigne). La app consume la API en `http://localhost:8000` — asegúrate de arrancar el backend primero.

3) Build para producción y preview local:

```powershell
npm run build
npm run preview
```

--

**Combinando backend + frontend**

1) Arranca el backend (ver sección Backend) en `:8000`.
2) Arranca el frontend (`npm run dev`) y abre `http://localhost:5173`.

La aplicación debería mostrar resultados semánticos, pósters (desde OMDb) y trailers (YouTube). Si los pósters no aparecen, revisa tu `OMDB_KEY`.

--

**Alternativas y notas sobre instalación en Windows (faiss / torch / sentence-transformers)**

- Problemas con `faiss-cpu` por pip en Windows: usar conda suele ser más sencillo.

Ejemplo con conda (recomendado si pip falla):

```powershell
conda create -n buscador python=3.10 -y
conda activate buscador
conda install -c conda-forge faiss-cpu -y
pip install -r backend/requirements.txt
```

- `sentence-transformers` instalará `torch`. Si quieres CPU-only y evitar versiones no compatibles, instala `torch` antes siguiendo las instrucciones oficiales de https://pytorch.org/.

--

**Problemas frecuentes y soluciones**

- Error al instalar `faiss-cpu` con pip en Windows: usa conda o WSL.
- Timeout/errores al consultar TMDB/OMDB: revisa tus claves y el acceso a internet; respeta límites de la API (sleep entre requests en `preprocess_dataset.py`).
- `Set-ExecutionPolicy` bloquea la activación del venv: ejecuta PowerShell como administrador y aplica `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` o usa CMD con `.\.venv\Scripts\activate`.
- Error al cargar el modelo: asegúrate de tener memoria suficiente; en máquinas con GPU la descarga/instalación puede usar versiones específicas de `torch`.

--

**Archivos y scripts importantes**

- `backend/api.py` : API FastAPI — punto de entrada.
- `backend/model_loader.py` : carga del modelo, índice FAISS y metadata desde `backend/data/`.
- `backend/preprocess_dataset.py` : script para enriquecer metadata (obtiene proveedores) y generar embeddings + FAISS en `backend/data/`.
- `backend/data/` : carpeta con artefactos (`metadata_es.csv`, `embeddings_es.npy`, `faiss_index_es.bin`, `providers_cache.json`).
- `frontend/` : app React con `src/` y componentes.

--

**Despliegue / Producción (guía rápida)**

- Generar los artefactos en un servidor con suficiente CPU/RAM.
- Construir frontend: `cd frontend && npm run build` y servir los archivos estáticos (Nginx, Netlify, Vercel, etc.).
- Servir backend con un servidor de procesos (gunicorn/uvicorn + systemd/PM2/servicio) y configurar HTTPS y variables de entorno.

--

**Licencia y créditos**

Proyecto educativo / demo. Ajusta y usa según tus necesidades. Algunas claves públicas de ejemplo están incluidas en los scripts — reemplázalas antes de exponer el servicio.

--

Si quieres, puedo:

- Ejecutar comprobaciones rápidas (buscar dependencias faltantes actuales).
- Añadir un script de PowerShell `scripts/setup-backend.ps1` para automatizar creación del venv e instalación.
- Crear instrucciones adicionales para desplegar con Docker/Compose.

¿Qué prefieres que haga ahora?
