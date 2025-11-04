from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.api.router import main_router
from backend.database.database import engine, Base

app = FastAPI()

#-------------For render-------------
#@app.on_event("startup")
#async def on_startup():
#    async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.create_all)
#-------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(main_router)

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="index.html")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)