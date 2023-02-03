"""IO Management for pygame interfaces
"""
import os
from IO import core
from IO.commandline import CursesController
import numpy as np
import asyncio
from websockets import serve
import threading
import time
import queue

import http.server
import socketserver


class FasiBoiHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, directory=os.path.join("resources", "misc", "webui"), **kwargs
        )


class Websocket:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.running = True
        self._websocket_instances = []
        self._output = queue.Queue()
        self._input = queue.Queue()

    def __enter__(self):
        self.thread = threading.Thread(
            target=self._async_run, args=self.args, kwargs=self.kwargs
        )
        self.thread.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.running = False
        self.thread.join()

    def send(self, data):
        self._output.put(data)

    def receive(self):
        return self._input.get()

    def unread_messages(self):
        return not self._input.empty()

    def _async_run(self, *args, **kwargs):
        asyncio.run(self._start_websocket(*args, **kwargs))

    async def _start_websocket(self, *args, **kwargs):
        async with serve(self._register, *args, **kwargs):
            while self.running:
                # send data
                while not self._output.empty():
                    data = self._output.get()
                    for websocket in self._websocket_instances:
                        if websocket.closed:
                            self._websocket_instances.remove(websocket)
                        else:
                            await websocket.send(data)

                    # receive data
                    for websocket in self._websocket_instances:
                        while len(websocket.messages) > 0:
                            msg = await websocket.recv()
                            self._input.put(msg)
                await asyncio.sleep(0.05)

    async def _register(self, websocket, path):
        self._websocket_instances.append(websocket)
        while self.running:
            await asyncio.sleep(1)


class WebDisplay(core.Display):
    """A Display for pygame gui windows"""

    def __init__(self, websocket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket = websocket
        self.full_refresh_threshold = self.width * self.height * 3 / 4

    def refresh(self):
        """Shows changes on the screen. Only updated pixels that have been changed
        since last call to this function.
        """
        self.websocket.send(self.pixels.tobytes().hex())


class WebController(core.Controller):
    """A Controller for command line inputs"""

    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket
        self.keymap = {
            "l": self.button_left,  # J
            "u": self.button_up,  # I
            "r": self.button_right,  # L
            "d": self.button_down,  # K
            "a": self.button_a,  # A
            "b": self.button_b,  # B
            "q": self.button_menu,  # Q
            "t": self.button_teppich,  # T
        }

    def update(self):
        """
        Updates its button according to the pressed key
        Args:
            char: The character representation of the pressed key
        """
        while self.websocket.unread_messages():
            msg = self.websocket.receive()
            msg_lower = msg.lower()
            if msg_lower in self.keymap:
                # uppercase: press, lowercase: release
                self.keymap[msg_lower].update(msg != msg.lower())


class WebIOManager(core.IOManager):
    """Pygame IO Manager"""

    def __init__(
        self,
        *args,
        bg_path=None,  # "resources/images/bg.png",
        title="FasiBoi-Color",
        screen_pos=(0, 0),  # (150, 100),
        screen_size=(500, 750),
        screen_res=(10, 15),
        **kwargs,
    ):

        self.websocket = Websocket("", 8001).__enter__()
        display = WebDisplay(self.websocket, *screen_res)
        controller = WebController(self.websocket)
        self.start_http()
        super().__init__(controller, display, *args, **kwargs)

    def start_http(self):
        PORT = 8000
        print(f"Serving on http://localhost:{PORT}")
        self.http_server = socketserver.TCPServer(("", PORT), FasiBoiHTTPRequestHandler)
        self.http_server_thread = threading.Thread(
            target=self.http_server.serve_forever
        )
        self.http_server.allow_reuse_address = True
        self.http_server_thread.start()
        print(f"Serving on http://localhost:{PORT}")

    def update(self):
        self.controller.update()

    def destroy(self):
        """Cleanup function that gets called after all applications are closed"""
        self.websocket.__exit__()
        print("Waiting for shutdown")
        self.http_server.server_close()
        self.http_server_thread.join()
        print("Shutdown http")
