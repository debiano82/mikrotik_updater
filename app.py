import sqlite3
import paramiko
import time
import logging
from datetime import datetime

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Nome del database
DB_NAME = 'mikrotik_devices.db'

def init_db():
    """Inizializza il database e crea la tabella se non esiste."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            current_version TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_device(ip, username, password):
    """Aggiunge un dispositivo al database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO devices (ip, username, password, current_version, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (ip, username, password, None, None))
    conn.commit()
    conn.close()
    logging.info(f"Dispositivo aggiunto: {ip}")

def get_devices():
    """Restituisce la lista di tutti i dispositivi."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, ip, username, password, current_version FROM devices')
    devices = cursor.fetchall()
    conn.close()
    return devices

def update_device_version(ip, version):
    """Aggiorna la versione del dispositivo nel database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE devices SET current_version = ?, last_updated = ? WHERE ip = ?
    ''', (version, datetime.now().isoformat(), ip))
    conn.commit()
    conn.close()

def ssh_connect(ip, username, password):
    """Connette via SSH al dispositivo MikroTik."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password, timeout=10)
        return client
    except Exception as e:
        logging.error(f"Errore connessione SSH a {ip}: {e}")
        return None

def get_routeros_version(client):
    """Ottiene la versione di RouterOS."""
    try:
        stdin, stdout, stderr = client.exec_command('/system resource print')
        output = stdout.read().decode('utf-8')
        for line in output.split('\n'):
            if 'version:' in line:
                version = line.split('version:')[1].strip()
                return version
    except Exception as e:
        logging.error(f"Errore nell'ottenere la versione: {e}")
    return None

def update_routeros(client):
    """Aggiorna RouterOS."""
    try:
        # Controlla aggiornamenti
        client.exec_command('/system package update check-for-updates')
        time.sleep(5)  # Aspetta

        # Installa aggiornamenti
        stdin, stdout, stderr = client.exec_command('/system package update install')
        output = stdout.read().decode('utf-8')
        logging.info(f"Aggiornamento installato: {output}")

        # Riavvia se necessario
        #client.exec_command('/system reboot')
        #logging.info("Riavvio del dispositivo.")
        #time.sleep(60)  # Aspetta riavvio
        return True
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento: {e}")
        return False

def update_device(ip, username, password):
    """Aggiorna un singolo dispositivo."""
    logging.info(f"Inizio aggiornamento per {ip}")
    client = ssh_connect(ip, username, password)
    if not client:
        return False

    # Ottieni versione corrente
    version = get_routeros_version(client)
    if version:
        update_device_version(ip, version)
        logging.info(f"Versione corrente: {version}")

    # Aggiorna
    success = update_routeros(client)
    client.close()
    if success:
        logging.info(f"Aggiornamento completato per {ip}")
    else:
        logging.error(f"Aggiornamento fallito per {ip}")
    return success

def main():
    init_db()

    while True:
        print("\nMikroTik Mass Update Tool")
        print("1. Aggiungi dispositivo")
        print("2. Visualizza dispositivi")
        print("3. Aggiorna tutti i dispositivi")
        print("4. Esci")
        choice = input("Scegli un'opzione: ").strip()

        if choice == '1':
            ip = input("Inserisci IP: ").strip()
            username = input("Inserisci username: ").strip()
            password = input("Inserisci password: ").strip()
            if ip and username and password:
                add_device(ip, username, password)
            else:
                print("Tutti i campi sono obbligatori.")
        elif choice == '2':
            devices = get_devices()
            if devices:
                print("Dispositivi nel database:")
                for device in devices:
                    print(f"ID: {device[0]}, IP: {device[1]}, User: {device[2]}, Version: {device[4] or 'N/A'}")
            else:
                print("Nessun dispositivo nel database.")
        elif choice == '3':
            devices = get_devices()
            if not devices:
                print("Nessun dispositivo nel database. Aggiungi dispositivi prima.")
                continue
            for device in devices:
                id_, ip, username, password, version = device
                update_device(ip, username, password)
                time.sleep(10)  # Pausa tra dispositivi
        elif choice == '4':
            break
        else:
            print("Opzione non valida.")

if __name__ == '__main__':
    main()