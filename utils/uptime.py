import humanize
import datetime

def get_uptime(launch_time: datetime.datetime) -> str:
    return humanize.naturaldelta(datetime.datetime.now() - launch_time)
