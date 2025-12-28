# MikroTik Mass Update Script

Questo script Python permette di aggiornare massivamente i router MikroTik tramite accesso SSH. Utilizza un database SQLite per gestire l'elenco degli IP, le credenziali e le versioni di RouterOS.

## Requisiti

- Python 3.x
- Libreria paramiko: `pip install paramiko`

## Installazione

1. Clona o scarica il progetto.
2. Installa le dipendenze: `pip install -r requirements.txt`

## Utilizzo

Esegui lo script: `python app.py`

Il programma presenta un menu interattivo con le seguenti opzioni:
1. **Aggiungi dispositivo**: Inserisci IP, username e password per aggiungere un nuovo dispositivo al database.
2. **Visualizza dispositivi**: Mostra la lista dei dispositivi salvati con IP, username e versione corrente.
3. **Aggiorna tutti i dispositivi**: Avvia il processo di aggiornamento per tutti i dispositivi nel database.
4. **Esci**: Chiudi il programma.

### Aggiungere Dispositivi
- Seleziona opzione 1 dal menu.
- Inserisci l'indirizzo IP del router MikroTik.
- Inserisci il nome utente SSH (di solito 'admin').
- Inserisci la password SSH.
- Il dispositivo verrà aggiunto al database SQLite.

## Database

Il database `mikrotik_devices.db` contiene una tabella `devices` con:
- id: ID univoco
- ip: Indirizzo IP del dispositivo
- username: Nome utente SSH
- password: Password SSH
- current_version: Versione RouterOS rilevata
- last_updated: Data e ora dell'ultimo aggiornamento

## Sicurezza

- Assicurati che le credenziali siano sicure.
- Usa chiavi SSH invece di password se possibile (modifica il codice di conseguenza).
- Testa su un dispositivo singolo prima dell'aggiornamento massivo.

## Note

- Gli aggiornamenti possono richiedere tempo e causare downtime.
- Monitora i log per eventuali errori.
- Adatta i comandi SSH se necessario per versioni specifiche di RouterOS.