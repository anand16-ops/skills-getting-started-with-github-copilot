import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(scope="session")
def client():
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_creates_new_participant(client):
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    assert response.status_code == 200
    assert new_email in response.json()["message"]

    activities = client.get("/activities").json()
    assert new_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup?email={existing_email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_success(client):
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants?email={email_to_remove}"
    )

    assert response.status_code == 200
    assert email_to_remove in response.json()["message"]

    activities = client.get("/activities").json()
    assert email_to_remove not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404(client):
    activity_name = "Chess Club"
    missing_email = "notregistered@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_missing_activity_returns_404(client):
    response = client.delete(
        "/activities/Nonexistent%20Club/participants?email=test@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
