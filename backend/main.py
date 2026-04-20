from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import energy
import traceback
import sys

app = FastAPI(title="LODANA API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBAL EXCEPTION HANDLER
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("!!! GLOBAL ERROR CAUGHT !!!", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()},
    )

@app.get("/")
async def root():
    return {"message": "LODANA API running"}

@app.get("/api/ping")
async def ping():
    return {"status": "pong"}

app.include_router(energy.router, prefix="/api", tags=["energy"])

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 is better for internal resolution
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
