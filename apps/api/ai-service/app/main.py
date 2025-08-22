from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import logging
from typing import List, Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai
from google.auth import default

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notes App AI Service", version="1.0.0")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

# Initialize Vertex AI
if PROJECT_ID:
    try:
        vertexai.init(project=PROJECT_ID, location=REGION)
        model = GenerativeModel(MODEL_NAME)
        logger.info(f"Initialized Vertex AI with model {MODEL_NAME} in {REGION}")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        model = None
else:
    logger.warning("GOOGLE_CLOUD_PROJECT not set, using mock AI responses")
    model = None

NOTES_SERVICE_URL = os.getenv("NOTES_SERVICE_URL", "http://localhost:8000/notes")
TASKS_SERVICE_URL = os.getenv("TASKS_SERVICE_URL", "http://localhost:8000/tasks")

class GenerateTitleRequest(BaseModel):
    body: str

class AIQueryRequest(BaseModel):
    query: str

async def generate_title_with_ai(body: str) -> str:
    """Generate a title using Vertex AI Gemini"""
    if not model:
        # Fallback to simple generation
        if body:
            words = body.split()[:8]
            return " ".join(words) + ("..." if len(body.split()) > 8 else "")
        return "Untitled Note"
    
    try:
        prompt = f"""Generate a concise, descriptive title (maximum 8 words) for the following note content. 
Return only the title, no additional text or formatting.

Note content:
{body[:500]}"""  # Limit content to avoid token limits
        
        response = model.generate_content(prompt)
        title = response.text.strip()
        
        # Clean up the response
        title = title.replace('"', '').replace("'", "").strip()
        
        # Ensure reasonable length
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title if title else "AI-Generated Note"
        
    except Exception as e:
        logger.error(f"Error generating title with AI: {e}")
        # Fallback to simple generation
        if body:
            words = body.split()[:8]
            return " ".join(words) + ("..." if len(body.split()) > 8 else "")
        return "Untitled Note"

@app.post("/generate_title")
async def generate_title(request: GenerateTitleRequest):
    """Generate a title for note content using AI"""
    try:
        title = await generate_title_with_ai(request.body)
        return {"title": title}
    except Exception as e:
        logger.error(f"Error in generate_title endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate title")

async def process_query_with_ai(query: str) -> dict:
    """Process natural language query using Vertex AI Gemini"""
    if not model:
        return await process_query_simple(query)
    
    try:
        # Use AI to understand the user's intent and extract structured data
        prompt = f"""You are a helpful assistant for a notes and tasks app. Analyze the following user query and respond with a JSON object containing:
1. "action": one of ["create_note", "find_note", "create_task", "find_task", "help", "unknown"]
2. "data": relevant extracted information based on the action

For create_note: {{"title": "extracted title", "body": "extracted content"}}
For find_note: {{"search_term": "what to search for"}}
For create_task: {{"description": "task description", "due_date": "YYYY-MM-DD or null"}}
For find_task: {{"search_term": "what to search for"}}
For help or unknown: {{"message": "helpful response"}}

User query: {query}

Respond only with valid JSON, no additional text."""
        
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        
        # Try to parse the JSON response
        try:
            import json
            parsed_response = json.loads(ai_response)
            return await execute_action(parsed_response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response: {ai_response}")
            return await process_query_simple(query)
            
    except Exception as e:
        logger.error(f"Error processing query with AI: {e}")
        return await process_query_simple(query)

async def process_query_simple(query: str) -> dict:
    """Fallback simple query processing"""
    query_lower = query.lower()
    
    if "create note" in query_lower:
        title = "New Note from AI"
        body = query.replace("create note", "").strip()
        if "with title" in body:
            parts = body.split("with title")
            title = parts[1].strip()
            body = parts[0].strip()
        return await create_note_action({"title": title, "body": body})
    
    elif "find note" in query_lower:
        search_term = query_lower.replace("find note about", "").replace("find note", "").strip()
        return await find_notes_action({"search_term": search_term})
    
    elif "create task" in query_lower:
        description = query.replace("create task", "").strip()
        return await create_task_action({"description": description, "due_date": None})
    
    elif "find task" in query_lower or "what are my tasks" in query_lower:
        search_term = query_lower.replace("find tasks about", "").replace("find tasks", "").replace("what are my tasks for", "").strip()
        return await find_tasks_action({"search_term": search_term})
    
    else:
        return {"message": "I can help you create and find notes or tasks. Try: 'create note about...', 'find note about...', 'create task to...', or 'what are my tasks?'"}

async def execute_action(parsed_response: dict) -> dict:
    """Execute the parsed action"""
    action = parsed_response.get("action")
    data = parsed_response.get("data", {})
    
    if action == "create_note":
        return await create_note_action(data)
    elif action == "find_note":
        return await find_notes_action(data)
    elif action == "create_task":
        return await create_task_action(data)
    elif action == "find_task":
        return await find_tasks_action(data)
    else:
        return {"message": data.get("message", "I'm not sure how to help with that.")}

async def create_note_action(data: dict) -> dict:
    """Create a note"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(NOTES_SERVICE_URL, json=data)
            response.raise_for_status()
            return {"message": "Note created successfully!", "note": response.json()}
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        return {"message": "Failed to create note. Please try again."}

async def find_notes_action(data: dict) -> dict:
    """Find notes"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NOTES_SERVICE_URL)
            response.raise_for_status()
            notes = response.json()
            
            search_term = data.get("search_term", "").lower()
            if search_term:
                found_notes = [note for note in notes if 
                             search_term in note["title"].lower() or 
                             search_term in note["body"].lower()]
            else:
                found_notes = notes
            
            if found_notes:
                return {"notes": found_notes, "count": len(found_notes)}
            else:
                return {"message": "No notes found matching your query."}
    except Exception as e:
        logger.error(f"Error finding notes: {e}")
        return {"message": "Failed to search notes. Please try again."}

async def create_task_action(data: dict) -> dict:
    """Create a task"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(TASKS_SERVICE_URL, json=data)
            response.raise_for_status()
            return {"message": "Task created successfully!", "task": response.json()}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"message": "Failed to create task. Please try again."}

async def find_tasks_action(data: dict) -> dict:
    """Find tasks"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(TASKS_SERVICE_URL)
            response.raise_for_status()
            tasks = response.json()
            
            search_term = data.get("search_term", "").lower()
            if search_term:
                found_tasks = [task for task in tasks if 
                             search_term in task["description"].lower()]
            else:
                found_tasks = tasks
            
            if found_tasks:
                return {"tasks": found_tasks, "count": len(found_tasks)}
            else:
                return {"message": "No tasks found matching your query."}
    except Exception as e:
        logger.error(f"Error finding tasks: {e}")
        return {"message": "Failed to search tasks. Please try again."}

@app.post("/query")
async def ai_query(request: AIQueryRequest):
    """Process natural language queries using AI"""
    try:
        result = await process_query_with_ai(request.query)
        return result
    except Exception as e:
        logger.error(f"Error in ai_query endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.get("/")
async def read_root():
    return {"message": "AI Service is running"}
