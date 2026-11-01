import socket
import json

# Configuracion del servidor
HOST = "localhost"
PORT = 5000


def enviar_tarea(sock, tipo, datos):
    peticion = json.dumps({"tarea": tipo, "datos": datos})
    sock.sendall((peticion + "\n").encode("utf-8"))
    respuesta = sock.recv(1024).decode("utf-8").strip()
    return json.loads(respuesta)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Conectado al servidor en {HOST}:{PORT}")

            while True:
                print("\n--- Envio de Tareas ---")
                print("1. Contar palabras")
                print("2. Invertir texto")
                print("3. Suma de 1 a N")
                print("4. Salir")
                opcion = input("Selecciona una opcion (1-4): ").strip()

                if opcion == "1":
                    texto = input("Ingresa el texto: ").strip()
                    res = enviar_tarea(s, "contar_palabras", texto)
                elif opcion == "2":
                    texto = input("Ingresa el texto a invertir: ").strip()
                    res = enviar_tarea(s, "invertir", texto)
                elif opcion == "3":
                    num = input("Ingresa el numero N: ").strip()
                    res = enviar_tarea(s, "calculo", num)
                elif opcion == "4":
                    s.sendall(b"salir\n")
                    print("Sesion finalizada.")
                    break
                else:
                    print("Opcion invalida.")
                    continue

                print(f"Respuesta del servidor: {res.get('resultado')} (tiempo: {res.get('duracion')}s)")

    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor. Asegurate de que este iniciado.")
    except KeyboardInterrupt:
        print("\nCliente finalizado por el usuario.")


if __name__ == '__main__':
    main()
