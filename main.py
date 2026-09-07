# ./.venv/bin/python -m uvicorn main:app --reload --port 8034

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from database import (
initialize_database,
insert_study_session,
get_study_session as get_study_session_from_db,
list_study_sessions,
list_study_sessions_by_subject as list_study_sessions_by_subject_from_db,
list_study_sessions_by_min_minutes,
list_study_sessions_by_subject_and_min_minutes,
delete_study_session as delete_study_session_from_db,
get_study_summary_by_subject as get_study_summary_by_subject_from_db,
update_study_session_minutes as update_study_session_minutes_from_db
)

app = FastAPI(title="Study Log API")

initialize_database()

class StudySessionCreate(BaseModel):
    subject: str = Field(..., min_length=1, description="Subject of the study")
    minutes: int = Field(..., gt=0,  description="Minutes of the study")

class StudySessionResponse(BaseModel):
    session_id: int
    subject: str
    minutes: int
    created_at: str

class StudySessionListResponse(BaseModel):
    count: int
    sessions: list[StudySessionResponse]

class StudySessionSummaryResponse(BaseModel):
    session_count: int
    total_minutes: int
    average_minutes: float

class StudySessionUpdate(BaseModel):
    minutes: int = Field(..., gt=0, description="Study minutes")

class SubjectSummaryResponse(BaseModel):
    subject: str
    session_count: int
    total_minutes: int

class SubjectSummaryListResponse(BaseModel):
    count: int
    subjects: list[SubjectSummaryResponse]

class DeleteStudySessionResponse(BaseModel):
    message: str
    session_id: int


@app.post("/api/v1/study-sessions", status_code=201, response_model=StudySessionResponse)
def create_study_session(request: StudySessionCreate):
    subject = request.subject.strip()
    minutes = request.minutes

    if not subject :
        raise HTTPException(status_code=400, detail="Subject cannot be blank")

    session_id = insert_study_session(subject, minutes)
    study_session = get_study_session_from_db(session_id)

    return study_session

@app.get("/api/v1/study-sessions", response_model=StudySessionListResponse)
def read_study_sessions(subject: str | None = Query(None, description="Study Subject"),
                        min_minutes: int | None = Query(None, gt=0, description="Minimum study minutes")
                        ):
    if subject is not None and min_minutes is not None:
        subject = subject.strip()
        sessions = list_study_sessions_by_subject_and_min_minutes(subject, min_minutes)

    elif subject is not None:
        subject = subject.strip()
        sessions = list_study_sessions_by_subject_from_db(subject)

    elif min_minutes is not None:
        sessions = list_study_sessions_by_min_minutes(min_minutes)

    else:
        sessions = list_study_sessions()

    count = len(sessions)

    return {
        "count": count,
        "sessions": sessions
    }

@app.get("/api/v1/study-sessions/summary", response_model=StudySessionSummaryResponse)
def read_study_session_summary():
    sessions = list_study_sessions()
    count = len(sessions)
    total_minutes = sum(session["minutes"] for session in sessions)
    if sessions:
        average_minutes = round(total_minutes / count, 2)

    else:
        average_minutes = 0
    return {
        "session_count": count,
        "total_minutes": total_minutes,
        "average_minutes": average_minutes
    }

@app.get("/api/v1/study-sessions/by-subject", response_model=SubjectSummaryListResponse)
def get_study_summary_by_subject():
    summaries = get_study_summary_by_subject_from_db()

    return {
        "count": len(summaries),
        "subjects": summaries
    }

@app.get("/api/v1/study-sessions/{session_id}", response_model=StudySessionResponse)
def get_study_session_by_id(session_id: int):
    session = get_study_session_from_db(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Study session not found")

    return session

@app.delete("/api/v1/study-sessions/{session_id}", response_model=DeleteStudySessionResponse)
def delete_study_session_by_id(session_id: int):
    session = get_study_session_from_db(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Study session not found")

    delete_study_session_from_db(session_id)

    return {
        "message": "Study session deleted successfully",
        "session_id": session_id
    }

@app.patch("/api/v1/study-sessions/{session_id}/minutes", response_model=StudySessionResponse)
def update_study_session_by_minutes(session_id: int, request: StudySessionUpdate):
    session = get_study_session_from_db(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Study session not found")

    update_study_session_minutes_from_db(session_id, request.minutes)

    session = get_study_session_from_db(session_id)

    return session

