# Helpdesk Backend (FastAPI + Azure CosmosDB for MongoDB)

## Wymagania
- Python 3.11+
- Azure CosmosDB for MongoDB vCore

## Instalacja

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Konfiguracja

Ustaw zmienne środowiskowe:

- `MONGODB_URL` — connection string do CosmosDB (np. `"mongodb://<username>:<password>@<host>:<port>/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@<user>@"`)
- `JWT_SECRET` — tajny klucz do JWT

Przykład pliku `.env.example`:

```
MONGODB_URL=mongodb://username:password@host:port/...
JWT_SECRET=supersecretkey
```

## Uruchomienie

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

W Azure Web App wskaż ścieżkę aplikacji:  
`app.main:app`

## Dokumentacja API

Po uruchomieniu:  
`http://<adres-serwera>/docs`