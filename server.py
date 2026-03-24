import socket
import sys


def visov_help():
    print("\nДоступные команды:")
    print("  LIST                 - показать список свободных мест")
    print("  BOOK <номер>         - забронировать место (номер от 1 до 10)")
    print("  HELP                 - показать эту подсказку")
    print("  quit                 - завершить работу клиента")
    print()

def otpravit_komandu(soket, komanda):
    soket.sendall((komanda + '\n').encode())
    data_bytes = b''
    while True:
        byt = soket.recv(1)
        if not byt:
            raise ConnectionError()
        data_bytes += byt
        if data_bytes.endswith(b'\n'):
            break
    otvet = data_bytes.decode().strip()
    print(otvet)
    return 1

def zapustit_klienta(host, port):
    try:
        soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soket.connect((host, port))
    except socket.error:
        print(f"Не удалось подключиться к серверу {host}:{port}")
        return
    print(f"Подключено к серверу {host}:{port}")
    visov_help()
    podklyucheno = 1
    while podklyucheno:
        user_input = input("> ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Завершение работы клиента")
            break
        elif user_input.lower() == "help":
            visov_help()
        else:
            try:
                podklyucheno = otpravit_komandu(soket, user_input)
            except (socket.error, ConnectionError):
                print("Ошибка связи с сервером. Возможно, сервер остановлен.")
                break
    soket.close()
    print("Соединение закрыто")

if __name__ == "__main__":
    host = "localhost"
    port = 12345
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    zapustit_klienta(host, port)
