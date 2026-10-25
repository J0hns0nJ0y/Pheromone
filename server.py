import asyncio, hashlib, json, os, time, urllib.request
from websockets.asyncio.server import serve, broadcast

CODES_URL = os.environ["CODES_URL"]
rooms = {}                      # code_hash -> {websocket: name}
fails = {}                      # ip -> [count, window_start]
cache = {"t": 0, "hashes": set()}

def load_hashes():
    if time.time() - cache["t"] > 20:
        with urllib.request.urlopen(CODES_URL, timeout=5) as r:
            cache["hashes"] = set(json.load(r))
        cache["t"] = time.time()
    return cache["hashes"]

def blocked(ip):
    c = fails.get(ip)
    return bool(c) and time.time() - c[1] < 300 and c[0] >= 5

def record_fail(ip):
    c = fails.get(ip)
    if not c or time.time() - c[1] >= 300:
        fails[ip] = [1, time.time()]
    else:
        c[0] += 1

async def handler(ws):
    ip = ws.request.headers.get("X-Forwarded-For", ws.remote_address[0]).split(",")[0].strip()
    if blocked(ip):
        await ws.send("ERR too many attempts, try later"); return
    try:
        first = json.loads(await asyncio.wait_for(ws.recv(), 10))
        code, name = str(first["code"]), str(first["name"])[:20]
    except Exception:
        return

    h = hashlib.sha256(code.encode()).hexdigest()
    try:
        valid = h in await asyncio.to_thread(load_hashes)
    except Exception:
        await ws.send("ERR server could not check codes"); return
    if not valid:
        record_fail(ip); await ws.send("ERR invalid code"); return

    room = rooms.setdefault(h, {})
    if len(room) >= 2:
        await ws.send("ERR room full"); return

    room[ws] = name
    await ws.send("OK")
    broadcast(room.keys(), f"* {name} joined ({len(room)}/2 in room)")
    try:
        async for msg in ws:
            broadcast([w for w in room if w is not ws], f"{name}: {str(msg)[:2000]}")
    finally:
        room.pop(ws, None)
        if room:
            broadcast(room.keys(), f"* {name} left")
        else:
            rooms.pop(h, None)          # room disappears, nothing was stored

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with serve(handler, "0.0.0.0", port):
        await asyncio.Future()

asyncio.run(main())