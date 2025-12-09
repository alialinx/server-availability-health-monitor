import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import tornado
from aiohttp import ClientSession
from pymongo.client_session import ClientSession
from pythonping import ping
from tornado.platform.asyncio import AsyncIOMainLoop

from app.database.database import get_db
from worker.send_mail import send_mail

db = get_db()
servers_collection = db.servers

from datetime import datetime
from zoneinfo import ZoneInfo

def generate_alert_body(server, result):
    now = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M:%S")
    body = f"""
    Server Alert!

    Date: {now}

    Server Name: {server.get('name')}
    IP / Host: {server.get('host')}
    Protocol: {server.get('protocol')}
    Port: {server.get('port')}
    Expected Status: {server.get('expected_status', 'N/A')}
    Last Check Result: {result}
    Description: {server.get('description', '-')}

    Please check the server.
    """
    return body.strip()



def parse_last_alert(last_alert):
    if not last_alert:
        return None

    if isinstance(last_alert, str):
        return datetime.strptime(last_alert, "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Istanbul"))
    if isinstance(last_alert, datetime):
        return last_alert.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Europe/Istanbul"))
    return last_alert


async def check_http(server):
    url = f"http://{server['host']}:{server.get('port', 80)}"
    expected_status = server.get('expected_status', 200)
    timeout = server.get('timeout', 5)

    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                status = response.status
                return status == expected_status, status
    except Exception as e:
        return False, str(e)


async def check_https(server):
    url = f"https://{server['host']}:{server.get('port', 443)}"
    expected_status = server.get('expected_status', 200)
    timeout = server.get('timeout', 5)

    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                status = response.status
                return status == expected_status, status
    except Exception as e:
        return False, str(e)


async def check_icmp(server):
    def ping_sync():
        response_list = ping(server['host'], count=1, timeout=server.get('timeout', 5))
        return response_list.success(), response_list.rtt_avg_ms

    return await asyncio.to_thread(ping_sync)


async def check_server(server):
    protocol = server['protocol'].lower()
    success, result = False, None

    if protocol == 'http':
        success, result = await check_http(server)
    elif protocol == 'https':
        success, result = await check_https(server)
    elif protocol == 'icmp':
        success, result = await check_icmp(server)

    now = datetime.now(ZoneInfo("Europe/Istanbul"))
    last_alert = parse_last_alert(server.get('last_alert_at'))

    alert_interval = server.get('alert_interval', 60)

    send_alert = False

    if not last_alert or (now - last_alert).total_seconds() > alert_interval * 60:
        send_alert = True

    if not success:
        if not last_alert or (now - last_alert).total_seconds() > alert_interval * 60:
            send_alert = True

    if send_alert:

        body = generate_alert_body(server, result)
        send_mail(server.get('contacts', []),f"Server Alert: {server['name']}",body,server_id=str(server["_id"])        )
        server['last_alert_at'] = now

    servers_collection.update_one({'_id': server['_id']}, {'$set': {'last_status': 'OK' if success else 'FAIL', 'last_checked_at': now, 'last_alert_at': server.get('last_alert_at')}})


async def monitor_loop():
    while True:
        servers = list(servers_collection.find({"is_active": True}))
        tasks = [check_server(s) for s in servers]
        await asyncio.gather(*tasks)
        await asyncio.sleep(30)


if __name__ == "__main__":
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_loop())
    tornado.ioloop.IOLoop.current().start()
