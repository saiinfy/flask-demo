import pytest

from app.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_list_items_starts_empty(client):
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_and_get_item(client):
    resp = client.post("/api/items", json={"name": "laptop"})
    assert resp.status_code == 201
    item = resp.get_json()
    assert item == {"id": 1, "name": "laptop"}

    resp = client.get(f"/api/items/{item['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "laptop"


def test_create_item_validation(client):
    resp = client.post("/api/items", json={})
    assert resp.status_code == 400
    resp = client.post("/api/items", json={"name": 123})
    assert resp.status_code == 400


def test_update_item(client):
    client.post("/api/items", json={"name": "old"})
    resp = client.put("/api/items/1", json={"name": "new"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "new"


def test_update_missing_item(client):
    resp = client.put("/api/items/99", json={"name": "x"})
    assert resp.status_code == 404


def test_delete_item(client):
    client.post("/api/items", json={"name": "temp"})
    assert client.delete("/api/items/1").status_code == 204
    assert client.get("/api/items/1").status_code == 404
    assert client.delete("/api/items/1").status_code == 404
