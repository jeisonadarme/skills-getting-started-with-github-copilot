from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic expected activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = "tester@example.com"

    # Ensure email not currently registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email not in data[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant added
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_signup_duplicate():
    activity = "Chess Club"
    email = "dup@example.com"

    # Make sure not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    if email in data[activity]["participants"]:
        # cleanup if leftover
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # First signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # Duplicate signup should return 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Cleanup
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup?email=someone@example.com")
    assert resp.status_code == 404


def test_unregister_nonexistent_participant_and_activity():
    activity = "Chess Club"
    email = "noone@example.com"

    # Ensure participant not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email not in data[activity]["participants"]

    # Unregistering a non-existent participant should return 404
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404

    # Unregistering on a non-existent activity should return 404
    resp = client.delete("/activities/NoSuchActivity/unregister?email=someone@example.com")
    assert resp.status_code == 404
