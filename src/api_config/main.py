"""
Simple FastAPI server for course creation.
Takes subject and difficulty level, returns complete course path.
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add course_path_generator directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'course_path_generator'))

# Import our course creation function
from src.course_path_generator.main_course_creator import create_complete_course
from src.db.mongo_client import get_database
import time
import uuid
from datetime import datetime

# Collections names (constants)
COURSE_COLLECTION = "content_coursePath"
TOPIC_COLLECTION = "content_topic"
# Best-guess defaults for user and progress collections; adjust via env if needed
USER_COLLECTION = os.getenv("USER_COLLECTION", "user")
PROGRESS_COLLECTION = os.getenv("PROGRESS_COLLECTION", "content_userCourseProgress")

def _persist_course_path(generation_result: dict, subject: str, difficulty: str, request_id: str, email: Optional[str] = None):
    """Transform and store the generated course path & topics into MongoDB.

    Mirrors the Spring Boot entity structure provided by user without changing generation logic.
    """
    try:
        db = get_database()
        data = generation_result.get("data", {})
        course_meta = data.get("coursePath", {})
        topics = data.get("topics", [])

        # Insert topics first and collect their IDs
        topic_ids = []
        topic_documents = []
        for t in topics:
            topic_id = t.get("id") or f"topic-{uuid.uuid4()}"
            video_info = t.get("videoInfo", {})
            topic_doc = {
                "_id": topic_id,
                "name": t.get("name"),
                "description": t.get("description"),
                "videoInfo": {
                    "youtubeUrl": video_info.get("youtubeUrl"),
                    "title": video_info.get("title"),
                    "startTime": video_info.get("startTime"),
                    "endTime": video_info.get("endTime"),
                },
                "prerequisites": t.get("prerequisites", []),
                "estimatedTimeMin": None,
                "tags": t.get("tags", [])
            }
            topic_documents.append(topic_doc)
            topic_ids.append(topic_id)

        if topic_documents:
            db[TOPIC_COLLECTION].insert_many(topic_documents)

        # Optional: find user by email to link creator and seed progress
        user_doc = None
        user_id = None
        user_display = None
        if email:
            try:
                user_doc = db[USER_COLLECTION].find_one({"email": email})
                if user_doc:
                    user_id = user_doc.get("_id") or user_doc.get("id")
                    user_display = user_doc.get("name") or user_doc.get("fullName") or email
            except Exception as ue:
                print(f"⚠️ User lookup failed for {email}: {ue}")

        # Build course document matching Spring Boot CoursePathEntity shape
        course_id = course_meta.get("id") or f"course-{uuid.uuid4()}"
        course_doc = {
            "_id": course_id,
            "creatorId": user_id,
            "title": course_meta.get("title", f"{subject} Learning Path"),
            "description": course_meta.get("description"),
            "targetLevel": course_meta.get("targetLevel", difficulty),
            "createdAt": int(time.time() * 1000),
            "createdBy": user_display or "analyzer-service",
            "topics": topic_ids,
            "reviews": [],
            "averageRating": None,
        }
        db[COURSE_COLLECTION].insert_one(course_doc)
        print(f"📦 Stored course {course_id} with {len(topic_ids)} topics in MongoDB")

        # If we have a user, add back-references and create progress document
        if user_id:
            try:
                # Add course to user's createdCoursePaths without duplicates
                db[USER_COLLECTION].update_one(
                    {"_id": user_id},
                    {"$addToSet": {"createdCoursePaths": course_id}}
                )
            except Exception as ue:
                print(f"⚠️ Failed to update user's createdCoursePaths for {user_id}: {ue}")

            # Enroll user into the newly created course
            try:
                db[USER_COLLECTION].update_one(
                    {"_id": user_id},
                    {"$addToSet": {"enrolledCoursePaths": course_id}}
                )
                print(f"📝 Enrolled user {user_id} into course {course_id}")
            except Exception as ue_enroll:
                print(f"⚠️ Failed to enroll user {user_id} into course {course_id}: {ue_enroll}")

            try:
                now_ms = int(time.time() * 1000)
                progress_id = f"progress-{uuid.uuid4()}"
                progress_entries = [
                    {
                        "topicId": tid,
                        "isCovered": False,
                        "lastUpdated": now_ms
                    }
                    for tid in topic_ids
                ]
                progress_doc = {
                    "_id": progress_id,
                    "userId": user_id,
                    "coursePathId": course_id,
                    "startedAt": now_ms,
                    "readiness": 0,
                    "progress": progress_entries
                }
                db[PROGRESS_COLLECTION].insert_one(progress_doc)
                print(f"🧭 Created progress {progress_id} for user {user_id} on course {course_id}")

                # Add progress reference to user's progress list
                try:
                    db[USER_COLLECTION].update_one(
                        {"_id": user_id},
                        {"$addToSet": {"courseProgressList": progress_id}}
                    )
                except Exception as ue2:
                    print(f"⚠️ Failed to update user's courseProgressList for {user_id}: {ue2}")
            except Exception as pe:
                print(f"⚠️ Failed to create progress for user {user_id}: {pe}")
    except Exception as e:
        print(f"❌ Persistence error: {e}")

def _background_generate_and_store(subject: str, difficulty: str, request_id: str, email: Optional[str] = None):
    """Background task wrapper that generates and persists the course path."""
    print(f"🛠️ Background generation started for request {request_id}")
    try:
        result = create_complete_course(subject=subject, difficulty_level=difficulty)
        if result.get("success"):
            _persist_course_path(result, subject, difficulty, request_id, email=email)
        else:
            print(f"⚠️ Generation failed for {request_id}: {result.get('error')}")
    except Exception as e:
        print(f"💥 Unhandled error during background generation {request_id}: {e}")
    print(f"✅ Background generation finished for request {request_id}")

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Skill mate ai analyzer API",
    description="API to create complete learning courses with AI-analyzed YouTube videos",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Request model
class CourseRequest(BaseModel):
    subject: str
    difficulty: str
    email: str | None = None  # Optional user email to link creator and initialize progress
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Python Programming",
                "difficulty": "beginner",
                "email": "user@example.com"
            }
        }

# Response model for success
class CourseResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None
    message: str = None

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Course Creator API is running!",
        "status": "healthy",
        "endpoints": {
            "generate_course_path": "POST /api/v1/generate-course-path",
            "health": "GET /api/v1/health",
            "docs": "GET /docs"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Course Creator API",
        "version": "1.0.0"
    }

@app.post("/api/v1/generate-course-path", status_code=status.HTTP_202_ACCEPTED)
async def create_course_endpoint(request: CourseRequest, background_tasks: BackgroundTasks):
    """Accept course generation request and process asynchronously.

    Returns 202 immediately with a requestId that can be used by the caller to later
    correlate stored course documents in MongoDB.
    """
    try:
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        if request.difficulty.lower() not in valid_difficulties:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}")
        if not request.subject or not request.subject.strip():
            raise HTTPException(status_code=400, detail="Subject cannot be empty")

        request_id = str(uuid.uuid4())
        print(f"⚡ Accepted generation request {request_id} for '{request.subject}' ({request.difficulty})")
        background_tasks.add_task(
            _background_generate_and_store,
            request.subject.strip(),
            request.difficulty.lower(),
            request_id,
            request.email
        )

        return {
            "success": True,
            "requestId": request_id,
            "status": "accepted",
            "message": "Course generation started. Poll MongoDB or future status endpoint for results.",
            "subject": request.subject.strip(),
            "difficulty": request.difficulty.lower(),
            "email": request.email
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"API Error (accept phase): {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Optional: Add more endpoints if needed

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv('PORT'))
    host = os.getenv('HOST')
    
    print(f"Starting Course Creator API on {host}:{port}")
    print(f"CORS Origins: {cors_origins}")
    print("API Documentation: http://127.0.0.1:8000/docs")
    
    # Use the app directly instead of reload for this setup
    uvicorn.run(
        "main:app",  # Use module:app format for reload to work
        host=host, 
        port=port,
        reload=False  # Disable reload when running directly
    )
