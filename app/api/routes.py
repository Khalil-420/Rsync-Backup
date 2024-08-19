from fastapi import APIRouter, BackgroundTasks, HTTPException,Query
from app.services.rsync_service import backup_servers, check_rsync_status
from app.core.config import Server
from app.db.server_db import *
from app.utils.cron import *
from app.utils.email import *
from app.services.rsync_service import *

router = APIRouter()

@router.post("/api/start_backup")
async def start_backup(background_tasks: BackgroundTasks):
    status = check_rsync_status()
    if status["status"] == "rsync is running":
        raise HTTPException(status_code=429, detail="Rsync is already running")
    backup_servers(background_tasks)
    return {"message": "Backup started"}


@router.get("/api/status", response_model=dict)
async def get_rsync_status():
    try:
        return check_rsync_status()
    except Exception as e:
        email_notification.put_error(str(e))



@router.post("/api/server", response_model=dict)
async def add_server(server: Server):
    try:    
        server_id = add_server_to_db(server)
        if server_id==0:
            return {"message": "Server already exist", "Server Host": server.host}
        return {"message": "Server added successfully", "server_id": server_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed Adding Server : Error {e}")



@router.delete("/api/server/{server_id}", response_model=dict)
async def remove_server(server_id: int):
    result = remove_server_from_db(server_id)
    if result:
        return {"message": "Server removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@router.get("/api/servers", response_model=List[dict])
async def get_servers(offset: int = Query(default=0, description="Offset for pagination"),
                      limit: int = Query(default=0, description="Limit the number of results")):
    servers = get_all_servers_from_db(offset=offset, limit=limit)
    return [dict(server) for server in servers]


@router.put("/api/server/{server_id}", response_model=dict)
async def update_server(server_id: int, update_data: ServerUpdate):
    update_result = update_server_in_db(server_id, update_data)
    return update_result
    
@router.post("/api/stop_cron", response_model=dict)
async def stop_cron(h: int):
    remove_cron_job(h)
    return {"message": "Cron Stopped Successfully"}


@router.post("/api/start_cron", response_model=dict)
async def start_cron(cron_request: CronRequest):
    remove_cron_job()
    create_cron_job(cron_request.h, cron_request.m)
    return {"message": "Cron Started Successfully"}


@router.get("/api/cron_status")
async def cron_status():
    try:
        crons = get_crons()
        return {"crons": crons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/api/migrate")
async def migrate(server_id:int,active:int=0):
    try:
        status = check_rsync_status()
        if status["status"] == "rsync is running":
            raise HTTPException(status_code=429, detail="Rsync is already running")
        migrate_server(server_id,active)
        return '{"message":"Migration Started Successfully"}'
    
    except:
        return '{"message":"Migration failed"}'
    
        
        