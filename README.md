# RechtChecker

## About The Project

Goal: Ask questions about your rights as a German.

Data used:

- [Grundgesetz](https://www.bundesregierung.de/resource/blob/974430/180722/b6c342e0e2f412d759a0a2a3af052a06/grundgesetz-data.pdf?download=1)
- [BGB](https://www.gesetze-im-internet.de/bgb/BGB.pdf)

### Installation

```
git clone https://github.com/AnnaKohlbecker/RechtChecker.git
```

## Getting Started

1. Make .env and fill missing variables

   ```bash
   cp .env.example .env
   ```

2. Install requirements

   ```
   pip install -r requirements.txt
   ```

3. Start Docker Desktop

4. Run Docker File

   ```
   docker-compose down -v
   docker-compose up -d
   docker ps
   ```

## Run

Run `main.py`
