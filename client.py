#!/usr/bin/env python

import asyncio
from websockets import connect


async def hello(uri):
    async with connect(uri) as websocket:
        await websocket.send("Hello world!")
        async for message in websocket:
            print(message)
            # await websocket.send("I received " + message)


asyncio.run(hello("ws://localhost:8765"))
