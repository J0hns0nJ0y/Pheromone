import asyncio, getpass, json, os, sys
from websockets.asyncio.client import connect

SERVER = "wss://yourpage.onrender.com"      # change to your host after deploying

async def main():
    code = getpass.getpass("Room code: ").strip()
    name = input("Your name: ").strip() or "guest"
    async with connect(SERVER) as ws:
        await ws.send(json.dumps({"code": code, "name": name}))
        reply = await ws.recv()
        if reply.startswith("ERR"):
            print(reply); return
        print("Connected. Type /quit to leave.\n")

        async def reader():
            async for msg in ws:
                print(msg)
            print("Disconnected."); os._exit(0)
        asyncio.create_task(reader())

        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line or line.strip() == "/quit":
                break
            if line.strip():
                await ws.send(line.strip())

asyncio.run(main())