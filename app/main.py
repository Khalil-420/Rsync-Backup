from fastapi import FastAPI
from app.api.routes import router
from app.utils.cron import *
from app.db.init_db import *
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    #On Startup
    create_cron_job()
    init_cron()
    start_db()
    yield
    #On Shutdown
    remove_cron_job()

app = FastAPI(lifespan=lifespan)

app.include_router(router)



    

