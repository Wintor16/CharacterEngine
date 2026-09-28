from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
import asyncio
from typing import Dict

from character.manager import CharacterManager
from config import settings
from core.engine import CharacterEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    manager = CharacterManager()
    character = manager.load(settings.DEFAULT_CHARACTER)
    engine = CharacterEngine(character)

    if os.environ.get("KURUMI_RESET_STATE") == "1":
        engine.reset_everything()
        print("[Reset - starting with a blank slate: no memories, default mood/relationship]")
    print(f"Kurumi AI initialized: {character.identity['name']}")
    yield


app = FastAPI(title="Kurumi Tokisaki AI", version="3.0", lifespan=lifespan)

# Setup templates - disable cache to avoid Jinja2 caching bug
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)

import jinja2
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(templates_dir)),
    autoescape=True,
    cache_size=0,  # Disable cache to avoid unhashable dict key bug
    enable_async=True
)

# Global engine instance
engine: CharacterEngine = None
active_connections: Dict[str, WebSocket] = {}


def render_template(template_name: str, context: dict) -> str:
    """Render template with custom env to avoid cache bug."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    template = jinja_env.get_template("index.html")
    html = await template.render_async(request=request)
    return HTMLResponse(content=html)


import concurrent.futures

# Thread pool for engine
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ... existing code ...

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    # Send welcome message
    welcome = {
        "type": "system",
        "content": "Connection established. The clock ticks...",
        "sender": "system"
    }
    await websocket.send_json(welcome)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                user_message = data.get("content", "")
                
                if user_message.lower() in ("exit", "quit", "bye"):
                    farewell = {
                        "type": "message",
                        "content": "Ara ara~ Leaving so soon? The shadows will miss you. *She fades into the darkness, her clock eye the last thing to vanish.*",
                        "sender": "kurumi",
                        "metadata": {"mood": "playful", "end": True}
                    }
                    await websocket.send_json(farewell)
                    break
                
                # Send thinking indicator
                thinking = {"type": "thinking", "content": "..."}
                await websocket.send_json(thinking)
                
                # Process through engine in thread pool with timeout
                try:
                    loop = asyncio.get_event_loop()
                    response = await asyncio.wait_for(
                        loop.run_in_executor(executor, engine.reply, user_message),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "type": "error",
                        "content": "*The shadows grow restless... The connection wavers.*",
                        "sender": "system",
                        "metadata": {"error": "timeout"}
                    })
                    continue
                
                if response.success:
                    # Determine mood from brain state
                    mood = "neutral"
                    if hasattr(engine, 'brain') and hasattr(engine.brain, 'state'):
                        mood = engine.brain.state.mood
                    
                    message_data = {
                        "type": "message",
                        "content": response.text,
                        "sender": "kurumi",
                        "metadata": {
                            "mood": mood,
                            "generation_time": response.generation_time,
                            "model": response.model
                        }
                    }
                    await websocket.send_json(message_data)
                else:
                    error_data = {
                        "type": "error",
                        "content": "*The connection wavers. The shadows flicker...*",
                        "sender": "system",
                        "metadata": {"error": response.error}
                    }
                    await websocket.send_json(error_data)
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_data = {
            "type": "error",
            "content": f"*A disturbance in time... {str(e)}*",
            "sender": "system"
        }
        await websocket.send_json(error_data)
    finally:
        if client_id in active_connections:
            del active_connections[client_id]


@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "character": "Kurumi Tokisaki",
        "model": settings.MODEL,
        "active_connections": len(active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.WEB_HOST, port=settings.WEB_PORT)