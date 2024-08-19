from crontab import CronTab
import subprocess
from app.utils.email import *
from app.core.config import *
from typing import Union, List, Dict


cron = CronTab(user="root")

def create_cron_job(h: Union[int, str] = '2', m: Union[int, str] = '0'):
    job = cron.new(command='curl -X POST http://localhost:8000/api/start_backup')
    job.setall(f'{m} {h} * * *') 
    
    cron.write()


def get_crons() -> List[Dict[str, str]]:
    jobs = []
    for job in cron:
        minutes = "".join([str(list(job.slices)[0]) if len(str(list(job.slices)[0]))==2 else f"0{str(list(job.slices)[0])}"])
        hours = "".join([str(list(job.slices)[1]) if len(str(list(job.slices)[1]))==2 else f"0{str(list(job.slices)[1])}"])
        jobs.append({"command": job.command, "schedule": f"Everyday at {hours}:{minutes}"})
    return jobs

def remove_cron_job(hours: int = 0):
    removed_jobs = []

    for job in cron:
        removed_jobs.append({"command": job.command, "schedule": str(job.slices)})
        cron.remove(job)
    
    cron.write()

    if hours > 0:
        def re_add_jobs():
            time.sleep(hours)
            for job_info in removed_jobs:
                job = cron.new(command=job_info["command"])
                job.setall(job_info["schedule"])
            cron.write()

        threading.Thread(target=re_add_jobs).start()



def init_cron():
    command = [
        "service", "cron", "start"
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result
