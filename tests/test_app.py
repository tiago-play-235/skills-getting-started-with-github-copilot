import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def client_and_reset():
    """Provide a TestClient and restore `activities` after each test."""
    original = copy.deepcopy(activities)
    with TestClient(app) as client:
        yield client
    activities.clear()
    activities.update(original)


def test_root_redirect(client_and_reset):
    # Arrange
    client = client_and_reset

    # Act
    r = client.get("/", follow_redirects=False)

    # Assert
    assert r.status_code == 307
    assert r.headers.get("location") == "/static/index.html"


def test_get_activities(client_and_reset):
    # Arrange
    client = client_and_reset

    # Act
    r = client.get("/activities")

    # Assert
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data


def test_signup_success_and_duplicate(client_and_reset):
    # Arrange
    client = client_and_reset
    email = "new_student@mergington.edu"

    # Act: successful signup
    r = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert successful signup
    assert r.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # Act: duplicate signup
    r2 = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert duplicate rejected
    assert r2.status_code == 400


def test_delete_participant_success_and_not_found(client_and_reset):
    # Arrange
    client = client_and_reset
    email = "to_remove@mergington.edu"

    # Act: add then remove
    add = client.post("/activities/Chess Club/signup", params={"email": email})
    r = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert removal succeeded
    assert add.status_code == 200
    assert r.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

    # Act: remove non-existent participant
    r2 = client.delete("/activities/Chess Club/participants", params={"email": "doesnotexist@x.com"})

    # Assert not found
    assert r2.status_code == 404


def test_unknown_activity_returns_404(client_and_reset):
    # Arrange
    client = client_and_reset

    # Act
    r = client.post("/activities/Nope/signup", params={"email": "a@b.c"})
    r2 = client.delete("/activities/Nope/participants", params={"email": "a@b.c"})

    # Assert
    assert r.status_code == 404
    assert r2.status_code == 404
