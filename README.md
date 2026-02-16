
## Přístup k implementaci

Během vývoje jsem vyhodnotil tři různé přístupy k generování zpráv o zápasech:

### Přístup 1: Ruční parsování a textové šablony
Analýza všech možných informací ze zápasu z Livesportu a naplnění detailní textové šablony extrahovanými daty.
- ❌ **Nevýhody**: Velmi časově náročná a nudná implementace; omezená flexibilita pro různé scénáře

### Přístup 2: Open Source LLM (DeepSeek)
Nasazení open-source LLM jako DeepSeek lokálně nebo přes API.
- ✅ **Výhody**: Potenciálně nižší náklady po dosažení určitého počtu volání API
- ❌ **Nevýhody**: Vyžaduje správu infrastruktury; méně spolehlivý pro složité úkoly

### Přístup 3: OpenAI API Agent (Vybrán ✓)
Implementace AI agenta pomocí GPT modelů od OpenAI k inteligentnímu generování zpráv o zápasech.
- ✅ **Výhody**: 
  - Spolehlivý a vysoce kvalitní výstup
  - Flexibilní a adaptivní na různé scénáře
  - Snadná integrace a údržba
  - Funguje dobře s GPT-4 i GPT-4o-mini modely
  - Efektivně škáluje se pro produkční použití
- ✅ **Nevýhody**: Model typu platba za použití (ale přijatelné náklady pro většinu případů)

## Struktura projektu

```
.
├── app.py                    # Hlavní Streamlit aplikace
├── agent.py                  # AI agent pro generování zpráv o zápasech
├── scraper.py                # Funkce web scrapingu
├── cleaner.py                # Utility pro čištění a normalizaci dat
├── storage.py                # Ukládání zpráv a správa souborů
├── schemas.py                # Schémata pro validaci dat (Pydantic)
├── config/
│   ├── configuration.py      # Konfigurace app a nastavení logování
│   ├── parameters.py         # Konfigurační parametry
│   └── prompts.py            # AI prompty pro generování zpráv
├── tests/
│   ├── test_agent.py         # Testy agenta
│   ├── test_scraper.py       # Unit testy scraperu
│   └── test_cleaner.py       # Testy utility pro čištění
├── outputs/                  # Vygenerované zprávy o zápasech (JSON soubory)
├── requirements.txt          # Python závislosti
├── Dockerfile                # Docker konfigurace
└── env_example               # Příklad proměnných prostředí
```

## Požadavky

- Python 3.12+
- OpenAI API klíč
- Požadované Python balíčky (viz requirements.txt)

## Instalace

1. **Klonujte repozitář**:
   ```bash
   git clone <repository-url>
   cd ls_26
   ```

2. **Vytvořte a aktivujte virtuální prostředí** (doporučeno):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

3. **Nainstalujte závislosti**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Nastavte proměnné prostředí**:
   ```bash
   cp env_example .env
   ```
   Upravte `.env` a přidejte váš OpenAI API klíč:
   ```plaintext
   OPENAI_API_KEY=your_actual_api_key_here
   MODE=prod  # nebo 'dev' pro debug režim
   ```

## Spuštění aplikace

### Lokální vývoj

Spusťte Streamlit aplikaci:
```bash
streamlit run app.py
```

Aplikace se otevře ve vašem prohlížeči na `http://localhost:8501`

### Režimy prostředí

- **Produkční režim** (`MODE=prod`): INFO úroveň logování
- **Vývojářský režim** (`MODE=dev`): DEBUG úroveň logování

### Docker

Sestavte a spusťte aplikaci v Dockeru:
```bash
docker build -t scoreflash .
docker run -p 8501:8501 --env-file .env scoreflash
```

## Spuštění testů

### Spuštění všech testů

```bash
pytest
```

### Spuštění konkrétního test souboru

```bash
pytest tests/test_scraper.py
pytest tests/test_agent.py
pytest tests/test_cleaner.py
```

## Přehled komponent

### `app.py`
Hlavní Streamlit aplikace poskytující webové rozhraní pro uživatele k zadání URL adres Livesportu a generování zpráv o zápasech.

### `agent.py`
Implementuje třídu `MatchReportAgent`, která orchestruje proces generování zpráv s použitím AI.

### `scraper.py`
Zpracovává web scraping stránek Livesportu k extrakci surových dat ze zápasů pomocí Playwrightu.

### `cleaner.py`
Poskytuje utility pro:
- Konverzi HTML na text
- Normalizaci URL
- Čištění a formátování dat ze zápasů

### `storage.py`
Spravuje ukládání vygenerovaných zpráv o zápasech do JSON souborů s pojmenováním na základě časových razítek.

### `schemas.py`
Definuje Pydantic datové modely pro validaci typů a serializaci zpráv o zápasech.

### `config/`
Správa konfigurace včetně nastavení logování, proměnných prostředí a AI promptů.

## Výstup

Vygenerované zprávy o zápasech jsou ukládány do adresáře `outputs/` s následující konvencí pojmenování:

```
YYYYMMDD_HHMMSS_Team1_vs_Team2.json
```

Příklad:
```
20260214_122122_Bohemians_vs_Mladá_Boleslav.json
```

## Řešení problémů

### Problémy s API klíčem
- Ujistěte se, že je `OPENAI_API_KEY` nastaven v souboru `.env`
- Ověřte, že je API klíč platný a má dostupnou kvótu

### Problémy se scrapingem
- Zkontrolujte, zda je URL adresa Livesportu platná
- Ujistěte se, že je připojení k internetu stabilní
- Prohlížeče Playwrightu může být nutné nainstalovat: `playwright install`

### Chyby importu
- Ověřte, že všechny balíčky v `requirements.txt` jsou nainstalovány
- Ujistěte se, že `PYTHONPATH` obsahuje kořen projektu
