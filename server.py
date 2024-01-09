import asyncio
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import logging

## Configuracion para la Raspberry Pi
from sense_hat import SenseHat
sense = SenseHat()


logging.basicConfig()

USERS = set()
MESSAGE = ''

# Evento usuarios
def users_event():
    print('users_event')
    # print(json.dumps({"type": "users", "count": len(USERS)}))
    
    if len(USERS) >= 1:
        print('Usuario conectado')
        print('Usuarios conectados: ' + str(len(USERS)))
    else:
        print('No hay usuarios conectados')
    
    return json.dumps({"type": "users", "count": len(USERS)})

# Evento mensajes
def value_event():
    # print('value_event')
    # print(json.dumps({"type": "value", "message": MESSAGE}))
    return MESSAGE


async def mensajes(websocket):
    global USERS, MESSAGE

    try:
        # Register user
        USERS.add(websocket)
        websockets.broadcast(USERS, users_event())
        websocket.send(value_event())
        
        # Manejar cambios de estado
        async for message in websocket:
            MESSAGE = message
            websockets.broadcast(USERS, value_event())
            print('Mensaje recibido: ' + message)
            sense.show_message(message)
            
    finally:
        # Desregistrar usuario
        USERS.remove(websocket)
        websockets.broadcast(USERS, users_event())

# Servidor WebSocket
async def main():
    async with websockets.serve(mensajes, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    print('Servidor WebSocket listo')
    asyncio.run(main())