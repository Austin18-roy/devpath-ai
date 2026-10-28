def test_root_endpoint(client):
    """Test the root endpoint redirects or provides entry points."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["health"] == "/api/v1/health"
    assert data["docs"] == "/api/v1/docs"


def test_health_endpoint(client):
    """Test the /api/v1/health endpoint returns 200 and expected schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "devpath-ai-backend"
    assert data["version"] == "0.1.0"
    assert "environment" in data
    assert "timestamp" in data


def test_cors_headers(client):
    """Test that CORS headers are returned for allowed origins."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/v1/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

