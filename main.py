import asyncio
import websockets
import json
import shortsocket
from state import State
from threading import Thread
# from uuid import uuid4
from websockets.exceptions import WebSocketException
from http import HTTPStatus
import struct
from admin import console
import re
import save
# from timer import Stopwatch
# from shortsocket import Array


state = None

tick_thread = None
admin_thread = None
save_thread = None


def create_status(data):
    return "S" + json.dumps(data)


def create_packet(data, response):
    msg_type = (b"R" if response else b"N")
    return msg_type + shortsocket.encode(data)


LOGIN = re.compile("login:(\w{3,20}),(\w{5,50});")
SIGNUP = re.compile("signup:(\w{3,20}),(\w{5,50});")


async def serve(websocket):
    # TODO: Verify client packets
    try:
        client = None
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                try:
                    message = message.decode("UTF-8")
                except UnicodeDecodeError:
                    message = ""
            login = LOGIN.fullmatch(message)
            signup = SIGNUP.fullmatch(message)
            if message == "ready":
                if client is not None:
                    await websocket.send(create_status({
                        "action": "ready"
                    }))
                    break
            elif login:
                client, msg = state.authorize(login.group(1), login.group(2))
                await websocket.send(create_status(msg))
            elif signup:
                client, msg = state.create_user(signup.group(1), signup.group(2))
                await websocket.send(create_status(msg))

        # client = state.create_user(uuid4())
        client.reset()
        keys = set()
        mouse_buttons = set()
        mouse_x = 0
        mouse_y = 0
        cell = 0
        mouse_wheel = 0
        async for message in websocket:
            if isinstance(message, str):
                message = message.encode("UTF-8")
            if message == b"exit":
                await websocket.close()
            else:
                msg_type = message[0]
                message = message[1:]
                if msg_type == ord("K"): # Keys
                    keys = {key for key in message}
                elif msg_type == ord("M"): # mouse Movement
                    mouse_x, mouse_y = struct.unpack("ff", message)
                elif msg_type == ord("B"): # mouse Buttons
                    msg = message[0]
                    mouse_buttons = set()
                    for i in list(range(3))[::-1]:
                        n = 1 << i
                        if n <= msg:
                            msg -= n
                            mouse_buttons.add(i + 1)
                elif msg_type == ord("W"): # mouse Wheel
                    mouse_wheel, = struct.unpack("f", message)
                elif msg_type == ord("C"): # selected Cell
                    cell = message[0] - 1
                    
                client.client_frame(
                    keys, mouse_buttons, mouse_x, mouse_y,
                    cell, mouse_wheel
                )
                mouse_wheel = 0
            for i in range(5):
                response = client.render_frame()
                if response:
                    packet = create_packet(
                        response, i == 0
                    )
                    await websocket.send(packet)
                else:
                    await websocket.send("F") # in the chat
    except WebSocketException:
        await websocket.close()


async def health_check(path, request_headers):
    if path != "/ws":
        return (
            HTTPStatus.FOUND, 
            {"Location": "https://puffio.repl.co" + path}, 
            b""
        )


async def start_server():
    async with websockets.serve(
        serve, 
        "0.0.0.0", 
        80,
        process_request=health_check,
    ):
        print("Server started!")
        state.server_started = True
        await asyncio.Future()


def main():
    global state, tick_thread, admin_thread, save_thread
    try:
        save.setup()
        
        state = save.load()
        if state is None:
            state = State()
        
        tick_thread = Thread(target=state.ticking)
        tick_thread.start()
        
        admin_thread = Thread(target=console, args=(state,))
        admin_thread.start()

        save_thread = Thread(target=save.repeat_save, args=(state,))
        save_thread.start()
        
        asyncio.run(start_server())
    except Exception as e:
        del state
        raise e


if __name__ == "__main__":
    main()
