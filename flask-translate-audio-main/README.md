# Flask Audio Transcription

Jednoduchá Flask aplikace pro nahrávání audio souborů a jejich přepis na text pomocí API.

## Struktura projektu

```
.
├── app.py              # Flask aplikace
├── requirements.txt    # Python závislosti
├── templates/         
│   ├── upload.html    # Formulář pro nahrání souboru
│   └── result.html    # Zobrazení výsledku přepisu
└── uploads/           # Složka pro dočasné audio soubory
```

## Instalace

1. Vytvořte a aktivujte virtuální prostředí:

```bash
# Vytvoření venv
python3 -m venv .venv

# Aktivace v Linux/macOS
source .venv/bin/activate

# Aktivace ve Windows
.venv\Scripts\activate
```

2. Instalace závislostí:

```bash
pip install -r requirements.txt
```

## Konfigurace

Aplikace používá konfigurační soubor `.env` pro nastavení proměnných prostředí. Výchozí hodnoty najdete v `.env.example`:

1. Zkopírujte šablonu do `.env`:
```bash
cp .env.example .env
```

2. Upravte hodnoty v `.env` podle potřeby:
```ini
# API Configuration
TRANSCRIBE_API_URL=http://192.168.22.141:9000
TRANSCRIBE_ENDPOINT=/transcribe
TRANSCRIBE_API_MANUAL=http://192.168.22.141:9010

# Flask Configuration
FLASK_SECRET=change-me-in-production
PORT=5000

# Upload Configuration
KEEP_UPLOADS=0
UPLOAD_DIR=uploads
```

Vysvětlení proměnných:

| Proměnná | Výchozí hodnota | Popis |
|----------|----------------|--------|
| `TRANSCRIBE_API_URL` | `http://192.168.22.141:9000` | URL transkripčního API serveru |
| `TRANSCRIBE_ENDPOINT` | `/transcribe` | Endpoint pro transkripci na API serveru |
| `TRANSCRIBE_API_MANUAL` | `http://192.168.22.141:9010` | URL manuálu API |
| `FLASK_SECRET` | `dev-secret` | Tajný klíč pro Flask session |
| `PORT` | `5000` | Port pro Flask server |
| `KEEP_UPLOADS` | `0` | Zachovat nahrané soubory (1=ano, 0=ne) |
| `UPLOAD_DIR` | `uploads` | Adresář pro nahrané soubory |

**Poznámka**: Soubor `.env` není verzován v gitu. Použijte `.env.example` jako šablonu.

## Spuštění

1. Aktivujte venv a spusťte aplikaci:

```bash
source .venv/bin/activate
python app.py
```

2. Otevřete prohlížeč na http://localhost:5000

## Použití

1. V prohlížeči vyberte audio soubor
2. Zvolte jazyk (`en` nebo `cz`)
3. Nastavte teplotu (0.0 - 1.0)
4. Klikněte na "Transcribe"
5. Výsledný přepis se zobrazí na další stránce

## API Dokumentace

- API Server: http://192.168.22.141:9000
- API Manuál: http://192.168.22.141:9010

## Řešení problémů

1. **404 Not Found**: Zkontrolujte `TRANSCRIBE_ENDPOINT` - musí odpovídat API serveru
2. **Connection Error**: Ověřte `TRANSCRIBE_API_URL` a dostupnost serveru
3. **Template Not Found**: Zkontrolujte že existuje složka `templates/` se soubory `upload.html` a `result.html`
4. **Permission Error**: Zkontrolujte práva pro zápis do složky `uploads/`

## Docker

### Rychlý start

```bash
# 1. Sestavení Docker image
docker build -t audio-transcribe .

# 2. Spuštění kontejneru na portu 5000
docker run -p 5000:5000 audio-transcribe

# Nyní otevřete http://localhost:5000 v prohlížeči
```

### Pokročilé spuštění

Pro produkční nasazení doporučujeme:

```bash
# Vytvoření .env souboru (pokud neexistuje)
cp .env.example .env

# Spuštění kontejneru s plnou konfigurací
docker run -d \
  --name flask-audio \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/uploads:/app/uploads \
  audio-transcribe
```

## Docker Compose

### Rychlý start s Docker Compose

```bash
# 1. Vytvoření .env (pokud neexistuje)
cp .env.example .env

# 2. Build a spuštění
docker compose up --build

# Pro spuštění na pozadí
docker compose up -d
```

### Užitečné příkazy

```bash
# Zobrazení logů
docker compose logs -f

# Zastavení služeb
docker compose down

# Restart služeb
docker compose restart

# Rebuild a restart
docker compose up -d --build
```

### Development prostředí

Pro vývoj můžete odkomentovat `web-dev` službu v `docker-compose.yml`:

```bash
# Spuštění vývojového prostředí na portu 5001
docker compose up web-dev
```

Vývojové prostředí obsahuje:
- Hot-reload při změně kódu
- Připojené zdrojové kódy
- Debug mód Flask
- Port 5001 (aby nekolidoval s produkcí)

### Parametry kontejneru

- Port: `5000` (produkce) nebo `5001` (vývoj)
- Volume: `./uploads:/app/uploads`
- Env soubor: `.env`
- Síť: `app-network` (bridge)

## CI/CD s GitHub Actions

Projekt obsahuje GitHub Actions workflow pro automatický build a push Docker image do GitHub Container Registry (ghcr.io).

### Nastavení

1. Povolte GitHub Actions ve vašem repozitáři
2. Povolte GitHub Packages pro váš repozitář
3. Workflow se spustí automaticky při:
   - Push do `main` větve
   - Vytvoření tagu `v*.*.*`
   - Pull requestu do `main`

### Docker Image tagy

- `latest` - poslední build z main větve
- `v1.0.0` - release tagy
- `sha-...` - konkrétní commit

## Kubernetes Deployment

### Prerekvizity

- Kubernetes cluster
- Nginx Ingress Controller
- Přístup ke ghcr.io (secrets)

### Nasazení

1. Vytvořte secret pro pull ghcr.io images:
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=GITHUB_USER \
  --docker-password=GITHUB_TOKEN
```

2. Upravte konfiguraci:
```bash
# Upravte hodnoty v k8s/config.yml
kubectl apply -f k8s/config.yml
```

3. Nasaďte aplikaci:
```bash
kubectl apply -f k8s/deployment.yml
```

### Konfigurace

Kubernetes manifesty obsahují:
- Deployment (2 repliky)
- Service (ClusterIP)
- Ingress (hostname routing)
- ConfigMap pro konfiguraci
- Secret pro citlivé údaje
- PVC pro uploads

### Monitoring

```bash
# Status deploymentu
kubectl get deployment audio-transcribe

# Logy
kubectl logs -l app=audio-transcribe

# Škálování
kubectl scale deployment audio-transcribe --replicas=3
```

### Produkční nastavení

Aplikace běží na gunicorn serveru s následující konfigurací:
- Bind na všechna rozhraní (`0.0.0.0:5000`)
- 2 worker procesy
- 4 thready na worker
- Thread-based worker (gthread)
- Access a error logy do stdout/stderr
- Využití /dev/shm pro temporary soubory

Pro úpravu gunicorn nastavení použijte proměnnou `GUNICORN_CMD_ARGS`, např.:
```bash
docker run -e GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=4" ...

### Správa kontejneru

```bash
# Zastavení
docker stop flask-audio

# Spuštění zastaveného
docker start flask-audio

# Odstranění
docker rm -f flask-audio
```

## Vývoj

- `.venv/` je v `.gitignore`
- Nahrané soubory jsou ve výchozím nastavení mazány po odeslání
- Pro zachování souborů nastavte `KEEP_UPLOADS=1`
- Pro vývoj v kontejneru můžete připojit zdrojové kódy: `-v $(pwd):/app`
