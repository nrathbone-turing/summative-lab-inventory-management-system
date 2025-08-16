from server import app

def test_health():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
