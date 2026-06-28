# 🌱 EcoSorter — Agente Visual Multimodal de Clasificación de Residuos

## 📌 Descripción
EcoSorter es un agente visual multimodal en tiempo real que ayuda a los usuarios a clasificar correctamente sus residuos. El usuario sostiene un objeto frente a la cámara y el sistema detecta, analiza y genera una respuesta inteligente indicando cómo preparar y desechar correctamente el residuo.

## 🔄 Flujo del Sistema
Cámara → YOLOv8 (Detección) → Gemini Vision (Análisis) → Respuesta Inteligente
## 🎯 Problema que Resuelve
Las personas frecuentemente dudan en qué contenedor depositar ciertos objetos o cómo prepararlos correctamente, lo que daña las cadenas de reciclaje.

## 🏗️ Arquitectura
- **Backend:** FastAPI + Python 3.12
- **Frontend:** Next.js 22 (Node)
- **Visión:** YOLOv8 + OpenCV
- **IA Multimodal:** Gemini Vision
- **Base de datos:** Supabase
- **Contenedores:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Cloud:** TBD (Render / Railway)

## 👥 Equipo
| Nombre | Rol |
|--------|-----|
| Anderson | Backend y Visión Computacional |
| Venus | Frontend y Especialista Multimodal |
| Camilo | Arquitecto Cloud y DevOps |
| Daniel | Scrum Master y QA |

## 🚀 Cómo ejecutar localmente

### Prerrequisitos
- Docker y Docker Compose instalados
- Clonar el repositorio

### Pasos
```bash
git clone https://github.com/AndresMZMZ/EcoSorter.git
cd EcoSorter
cp .env.example .env
# Editar .env con tus credenciales
docker-compose up --build
```

### Acceso
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Docs API: `http://localhost:8000/docs`

## 🔐 Variables de Entorno
Ver `.env.example` para referencia.

## 🧪 Pruebas
```bash
cd backend
pytest app/tests/ --cov=app --cov-report=term-missing
```

## 📋 Gestión del Proyecto
El proyecto se gestiona con metodología **Scrum** usando **Jira**.

## 📄 Licencia
MIT