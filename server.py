import socket
import threading
import sys


KOLICHESTVO_MEST = 10
mesta = [1] * KOLICHESTVO_MEST

def pestoi_mesta():
    free_mesto = []
    i = 0
    while i < KOLICHESTVO_MEST:
        if mesta[i] == 1:
            free_mesto.append(str(i + 1))
        i += 1
    if not free_mesto:
        return "свободных мест нет"
    return " ".join(free_mesto)

def zabronirovat_mesto(nomer_mesta):
    if nomer_mesta < 1 or nomer_mesta > KOLICHESTVO_MEST:
        return 0, "Неверный номер места"
    idx = nomer_mesta - 1
    if mesta[idx] == 1:
        mesta[idx] = 0
        return 1, "Место успешно забронировано"
    else:
        return 0, "Место уже занято"

def obrabotat_komandu(cmd):
    chasti = cmd.split()
    if not chasti:
        return "ERROR пустая команда"
    komanda = chasti[0].upper()
    if komanda == "LIST":
        free_str = pestoi_mesta()
        return f"OK свободные места: {free_str}"
    elif komanda == "BOOK":
        if len(chasti) != 2:
            return "ERROR формат: BOOK <номер_места>"
        try:
            nomer_mesta = int(chasti[1])
        except ValueError:
            return "ERROR номер места должен быть целым числом"
        uspeh, soobshenie = zabronirovat_mesto(nomer_mesta)
        if uspeh:
            status = "OK"
        else:
            status = "ERROR"
        return status + " " + soobshenie
    else:
        return "ERROR неизвестная команда"

def obrabotat_klienta(klient_soket, adres_klienta, rabotaet, soedineniya_klientov, blokirovka):
    klient_soket.settimeout(1.0)
    while rabotaet[0]:
        try:
            data_bytes = b''
            while True:
                byt = klient_soket.recv(1)
                if not byt:
                    raise ConnectionError()
                data_bytes += byt
                if data_bytes.endswith(b'\n'):
                    break
            komanda = data_bytes.decode().strip()
            if komanda:
                print(f"Получено от {adres_klienta}: {komanda}")
                otvet = obrabotat_komandu(komanda)
                klient_soket.sendall((otvet + '\n').encode())
        except socket.timeout:
            continue
        except (ConnectionError, socket.error):
            break
    klient_soket.close()
    blokirovka.acquire()
    if klient_soket in soedineniya_klientov:
        soedineniya_klientov.remove(klient_soket)
    blokirovka.release()
    print(f"Клиент {adres_klienta} отключился")

def zapustit_server(host, port):
    server_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_soket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_soket.bind((host, port))
    server_soket.listen(5)
    print(f"Сервер запущен на {host}:{port}")
    print("Для остановки сервера введите 'stop'")
    rabotaet = [1]
    soedineniya_klientov = []
    blokirovka = threading.Lock()
    potoki = []

    def prinimat_klientov():
        while rabotaet[0]:
            try:
                klient_soket, adres = server_soket.accept()
                if not rabotaet[0]:
                    break
                print(f"Новое подключение от {adres}")
                blokirovka.acquire()
                soedineniya_klientov.append(klient_soket)
                blokirovka.release()
                t = threading.Thread(
                    target=obrabotat_klienta,
                    args=(klient_soket, adres, rabotaet, soedineniya_klientov, blokirovka)
                )
                t.start()
                potoki.append(t)
            except socket.error:
                break
    potok_prinima = threading.Thread(target=prinimat_klientov)
    potok_prinima.start()
    while rabotaet[0]:
        cmd = sys.stdin.readline().strip()
        if cmd.lower() == "stop":
            print("Останавливаем сервер...")
            rabotaet[0] = 0
            break
    server_soket.close()
    blokirovka.acquire()
    for soket in soedineniya_klientov:
        soket.close()
    blokirovka.release()
    potok_prinima.join()
    for t in potoki:
        t.join(timeout=1)
    print("Сервер остановлен")

if __name__ == "__main__":
    host = "localhost"
    port = 12345
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        KOLICHESTVO_MEST = int(sys.argv[3])
        mesta = [1] * KOLICHESTVO_MEST
    zapustit_server(host, port)
