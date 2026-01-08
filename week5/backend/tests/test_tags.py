from backend.app.models import Tag


def test_tags_crud(client):
    # Initially empty
    r = client.get("/tags")
    assert r.status_code == 200
    assert r.json() == []

    # Create a tag
    r = client.post("/tags", json={"name": "work"})
    assert r.status_code == 201, r.text
    tag = r.json()
    assert tag["name"] == "work"
    tag_id = tag["id"]

    # List should include the tag
    r = client.get("/tags")
    assert r.status_code == 200
    tags = r.json()
    names = [t["name"] for t in tags]
    assert "work" in names

    # Creating a duplicate tag should fail
    r = client.post("/tags", json={"name": "work"})
    assert r.status_code == 400

    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    # It should no longer appear in the list
    r = client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "work" not in names

    # Deleting again should return 404
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 404
