"""
Simple FastAPI server for course creation.
Takes subject and difficulty level, returns complete course path.
"""

import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add course_path_generator directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'course_path_generator'))

# Import our course creation function
from src.course_path_generator.main_course_creator import create_complete_course

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
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Python Programming",
                "difficulty": "beginner"
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
            "create_course": "POST /create-course",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Course Creator API",
        "version": "1.0.0"
    }

@app.post("/api/v1/generate-course-path", response_model=CourseResponse)
async def create_course_endpoint(request: CourseRequest):
    
    try:
        # Validate difficulty level
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        if request.difficulty.lower() not in valid_difficulties:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}"
            )
        
        # Validate subject
        if not request.subject or not request.subject.strip():
            raise HTTPException(
                status_code=400,
                detail="Subject cannot be empty"
            )
        
        # Create the course
        print(f"API: Creating course for '{request.subject}' at {request.difficulty} level")
        
        course_path = create_complete_course(
            subject=request.subject.strip(),
            difficulty_level=request.difficulty.lower()
        )
        
        # Check if course creation was successful
        if course_path.get('success'):
            return CourseResponse(
                success=True,
                data=course_path.get('data'),
                message="Course created successfully!"
            )
        else:
            return CourseResponse(
                success=False,
                error=course_path.get('error', 'Unknown error occurred'),
                message="Course creation failed"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        return CourseResponse(
            success=False,
            error=str(e),
            message="Internal server error occurred"
        )

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
