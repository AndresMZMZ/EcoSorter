from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test 1: Verifica que el endpoint raiz retorne HTTP 200 y el mensaje de bienvenida."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to EcoSorter API. Ready for Sprint 1!"}

def test_classify_endpoint_success():
    """Test 2: Verifica que POST /classify retorne HTTP 200 con estructura de clasificacion exitosa."""
    payload = {"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."}
    response = client.post("/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "label" in data
    assert "veredicto" in data
    assert "preparacion" in data

def test_classify_endpoint_invalid_method():
    """Test 3: Verifica que usar un metodo HTTP incorrecto (GET) en /classify retorne HTTP 405 (Method Not Allowed)."""
    response = client.get("/classify")
    assert response.status_code == 405

def test_classify_endpoint_empty_payload():
    """Test 4: Verifica que enviar un payload vacio en POST /classify sea recibido por la API sin fallos de servidor (HTTP 200 o HTTP 422 si validara esquema)."""
    # Como la API actual recibe dict generico, debe retornar 200 y el mock
    response = client.post("/classify", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_cors_headers():
    """Test 5: Verifica que las cabeceras CORS de control de acceso esten configuradas para el frontend."""
    # Hacemos una peticion de opciones (Preflight) o una peticion normal
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"
