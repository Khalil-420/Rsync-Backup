import subprocess
from fastapi import BackgroundTasks, APIRouter, HTTPException
from app.core.config import settings, Server
from app.utils.email import *
from app.db.server_db import *
import psutil
import os
from datetime import datetime
import paramiko


email_notification = Email()

ssh_key_path = os.getenv('SSH_KEY_PATH')


def run_rsync(remote_path: str, local_path: str, user: str, host: str, name: str):
    try:
        command = [
            "rsync",
            "-avz",
            "--delete",
            "-e", f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no",
            f"{user}@{host}:{remote_path}",
            local_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Running Rsync Failed On: {name}, Error: {e}, Time: {timestamp}"
        email_notification.put_error(error_message)


def stop_docker_compose(host: str, user: str, name: str):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        command = "docker ps -qa | xargs docker stop"
        client.connect(hostname=host, username=user, key_filename=ssh_key_path)
        _stdin, _stdout,_stderr = client.exec_command(command)
        errors = _stderr.read().decode()
        if errors:
            raise errors
        return
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Stopping Docker Failed On: {name}, Errors: {e}, Time: {timestamp}"
        email_notification.put_error(error_message)


def start_docker_compose(host: str, user: str, name: str):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        command = "docker ps -qa | xargs docker start"
        client.connect(hostname=host, username=user, key_filename=ssh_key_path)
        _stdin, _stdout,_stderr = client.exec_command(command)
        errors = _stderr.read().decode()
        return
    except:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Starting Docker Failed On: {name}, Error: {errors}, Time: {timestamp}"
        email_notification.put_error(error_message)
        
        
def backup_server(server: Server):
    try:
        stop_result = stop_docker_compose(server.host, server.user, server.name)
        if stop_result:
            local_path = f"{settings.backup_root_path}/{server.local_folder}"
            run_rsync(
                server.remote_path,
                local_path,
                server.user,
                server.host,
                server.name
            )
            start_docker_compose(server.host, server.user, server.name, server.remote_path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_notification.send(subject="Backup Successfull",body=f"{server.name} BackUp Succesfully At {timestamp}")
        else:
            return
        return
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Failed Backuping Server: {server.name}, Error: {e}, Time: {timestamp}"
        email_notification.put_error(error_message)
            


def backup_servers(background_tasks: BackgroundTasks):
    try:
        servers = get_all_servers_from_db()
        for server in servers:
            server_create = Server(
                name=server["name"],
                host=server["host"],
                user=server["user"],
                remote_path=server["remote_path"],
                local_folder=server["local_folder"]
            )
            background_tasks.add_task(backup_server, server_create)
    except Exception as e:
            email_notification.put_error(f"Backuping Servers Failed : {server_create.name}")
            raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

def check_rsync_status():
    # Check if rsync is running
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'rsync':
            return {"status": "rsync is running","health":"system is up"}

    # If no rsync process found
    return {"status": "rsync is not running","health":"system is up"}

def run_rsync_migrate(remote_path: str, local_path: str, user: str, host: str, name: str):
    try:
        command = [
            "rsync",
            "-avz",
            "--delete",
            "-e", f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no",
            local_path,f"{user}@{host}:{remote_path}",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Running Rsync Failed On: {name}, Error: {e}, Time: {timestamp}"
        email_notification.put_error(error_message)
        
def migrate_server(server_id: int,active:int):
    try:
        server = fetch_server_by_id(server_id)
        if server:
            if active:
                stop_docker_compose(server.host, server.user, server.name)
            local_path = f"{settings.backup_root_path}/{server.local_folder}"
            run_rsync_migrate(
                        server.remote_path,
                        local_path,
                        server.user,
                        server.host,
                        server.name
                    )
            if active:
                start_docker_compose(server.host, server.user, server.name, server.remote_path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_notification.send(subject="Migration Successfull",body=f"{server.name} Migration Succesfully At {timestamp}")
            return
        else:
            raise HTTPException(status_code=404, detail="No server matches with that id")
    except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_message = f"Failed Migration Server: {server.name}, Error: {e}, Time: {timestamp}"
                email_notification.put_error(error_message)