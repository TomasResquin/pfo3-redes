import socket
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuracion del servidor
HOST = "localhost"
PORT = 5000
MAX_WORKERS = 4

# Pool de workers para procesar tareas en segundo plano
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


def procesar_tarea(tipo_tarea, datos):
    # Simula el procesamiento de una tarea en un worker
    inicio = time.time()

    if tipo_tarea == "contar_palabras":
        texto = str(datos)
        resultado = len(texto.split())
    elif tipo_tarea == "invertir":
        resultado = str(datos)[::-1]
    elif tipo_tarea == "calculo":
        # Suma de 1 a n
        try:
            n = int(datos)
            resultado = sum(range(1, n + 1))
        except ValueError:
            resultado = "Dato no numerico"
    else:
        resultado = f"Tarea desconocida: {tipo_tarea}"

    duracion = round(time.time() - inicio, 4)
    return {"resultado": resultado, "duracion": duracion}


def atender_cliente(conn, addr):
    print(f"Cliente conectado desde {addr}")
    try:
        while True:
            datos = conn.recv(1024)
            if not datos:
                break

            mensaje = datos.decode("utf-8").strip()
            if mensaje.lower() in ["salir", "exit"]:
                break

            try:
                peticion = json.loads(mensaje)
                tipo = peticion.get("tarea", "")
                parametro = peticion.get("datos", "")

                print(f"[{addr}] Tarea recibida: {tipo} -> enviando a pool de workers")

                # Asignar la tarea a un worker del pool
                futuro = executor.submit(procesar_tarea, tipo, parametro)
                respuesta_datos = futuro.result()

                respuesta = json.dumps({
                    "estado": "completado",
                    "tarea": tipo,
                    "resultado": respuesta_datos["resultado"],
                    "duracion": respuesta_datos["duracion"]
                })
            except json.JSONDecodeError:
                respuesta = json.dumps({"estado": "error", "mensaje": "JSON invalido"})

            conn.sendall((respuesta + "\n").encode("utf-8"))

    except ConnectionResetError:
        print(f"El cliente {addr} cerro la conexion inesperadamente.")
    finally:
        conn.close()
        print(f"Conexion cerrada con {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"Servidor escuchando en {HOST}:{PORT} (Workers disponibles: {MAX_WORKERS})...")

        try:
            while True:
                conn, addr = servidor.accept()
                # Atiende la conexion en un hilo dedicado para no consumir workers del pool
                hilo_cliente = threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True)
                hilo_cliente.start()
        except KeyboardInterrupt:
            print("\nServidor detenido por el usuario.")
        finally:
            executor.shutdown(wait=False)


if __name__ == '__main__':
    main()
