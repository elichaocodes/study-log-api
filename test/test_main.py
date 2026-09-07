import os
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

TEST_DATABASE_PATH = Path(__file__).with_name("test_study_session.db")
os.environ["DATABASE_PATH"] = str(TEST_DATABASE_PATH)

from main import app
from database import initialize_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_study_log():
    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()

    initialize_database()

def test_create_study_session():
    response = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python",
                               "minutes": 45
                           }
                           )

    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == 1
    assert data["subject"] == "Python"
    assert data["minutes"] == 45

    response = client.get("/api/v1/study-sessions")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1

def test_get_study_session_by_id():
    response = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python",
                               "minutes": 45
                           }
                           )
    assert response.status_code == 201
    create_data = response.json()
    session_id = create_data["session_id"]

    response = client.get(f"/api/v1/study-sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["subject"] == "Python"
    assert data["minutes"] == 45

def test_get_study_session_rejects_unknown_id():
    response = client.get("/api/v1/study-sessions/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Study session not found"

def test_get_study_session_summary():
    response1 = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python1",
                               "minutes": 45
                           }
                           )

    response2 = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python2",
                               "minutes": 30
                           }
                           )
    assert response1.status_code == 201
    assert response2.status_code == 201

    response = client.get("/api/v1/study-sessions/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["session_count"] == 2
    assert data["total_minutes"] == 75
    assert data["average_minutes"] == 37.5

def test_get_study_session_summary_returns_zero_when_empty():
    response = client.get("/api/v1/study-sessions/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["session_count"] == 0
    assert data["total_minutes"] == 0
    assert data["average_minutes"] == 0

def test_study_subject_Query():
    response1 = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python",
                               "minutes": 45
                           }
                           )
    response2 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "English",
                                "minutes": 30
                            }
                            )
    response3 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 60
                            }
                            )
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    response = client.get("/api/v1/study-sessions",
                          params={
                              "subject": "Python",
                          }
                          )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["sessions"][0]["subject"] == "Python"
    assert data["sessions"][1]["subject"] == "Python"
    assert data["sessions"][0]["minutes"] == 60

def test_combine_study_sessions():
    response1 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 45
                            }
                            )
    response2 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "English",
                                "minutes": 30
                            }
                            )
    response3 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 60
                            }
                            )
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    response = client.get("/api/v1/study-sessions",
                          params={
                              "subject": "Python",
                              "min_minutes": 50
                          }
                          )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["sessions"][0]["subject"] == "Python"
    assert data["sessions"][0]["minutes"] == 60

def test_min_minutes_Query():
    response1 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 45
                            }
                            )
    response2 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "English",
                                "minutes": 30
                            }
                            )
    response3 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 60
                            }
                            )
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    response = client.get("/api/v1/study-sessions",
                          params={
                              "min_minutes": 40
                          }
                          )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["sessions"][0]["minutes"] >= 40
    assert data["sessions"][1]["minutes"] >= 40

    # assert all(
    #     session["minutes"] >= 40
    #     for session in data["sessions"]
    # )

def test_return_empty_list():
    response = client.get("/api/v1/study-sessions?subject=Math")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["sessions"] == []

def test_delete_study_session():
    response = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 45
                            }
                            )
    assert response.status_code == 201

    create_data = response.json()
    session_id = create_data["session_id"]

    response = client.delete(f"/api/v1/study-sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Study session deleted successfully"
    assert data["session_id"] == session_id

    response = client.get(f"/api/v1/study-sessions/{session_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Study session not found"

def test_delete_nonexistent_study_session():
    response = client.delete("/api/v1/study-sessions/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Study session not found"

def test_get_study_summary_by_subject():
    response1 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 45
                            }
                            )
    response2 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "English",
                                "minutes": 30
                            }
                            )
    response3 = client.post("/api/v1/study-sessions",
                            json={
                                "subject": "Python",
                                "minutes": 60
                            }
                            )
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    response = client.get("/api/v1/study-sessions/by-subject")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["subjects"][0]["subject"] == "Python"
    assert data["subjects"][0]["session_count"] == 2
    assert data["subjects"][0]["total_minutes"] == 105
    assert data["subjects"][1]["subject"] == "English"
    assert data["subjects"][1]["session_count"] == 1
    assert data["subjects"][1]["total_minutes"] == 30

def test_update_study_session_by_minute():
    response = client.post("/api/v1/study-sessions",
                           json={
                               "subject": "Python",
                               "minutes": 45
                           }
                           )
    assert response.status_code == 201
    create_data = response.json()
    session_id = create_data["session_id"]

    response_a = client.patch(f"/api/v1/study-sessions/{session_id}/minutes",
                            json={
                                "minutes": 60
                            }
                            )
    assert response_a.status_code == 200
    data = response_a.json()
    assert data["minutes"] == 60

    response_b = client.get(f"/api/v1/study-sessions/{session_id}")
    assert response_b.status_code == 200
    data = response_b.json()
    assert data["minutes"] == 60

def test_update_nonexistent_study_session_rejects_request():
    response = client.patch("/api/v1/study-sessions/999/minutes",
                            json={
                                "minutes": 60
                            }
                            )

    assert response.status_code == 404
    assert response.json()["detail"] == "Study session not found"