# TP FINAL SD - CI/CD Workflows

En esta carpeta encontrarás los workflows de CI/CD para cada componente, listos para usar con GitHub Actions o `act` local:

## Archivos
- `02-mover.yml`
- `03-validator.yml`
- `04-pool.yml`
- `05-worker-mocks.yml`
- `06-frontend.yml`

## Comandos para probar localmente con `act`

```bash
cd tpFinal

# Asegúrate de tener .env.secrets en tpFinal/
# Luego ejecuta cada workflow:
act -W ./.github/workflows/02-mover.yml --secret-file .env.secrets --pull=false
act -W ./.github/workflows/03-validator.yml --secret-file .env.secrets --pull=false
act -W ./.github/workflows/04-pool.yml --secret-file .env.secrets --pull=false
act -W ./.github/workflows/05-worker-mocks.yml --secret-file .env.secrets --pull=false
act -W ./.github/workflows/06-frontend.yml --secret-file .env.secrets --pull=false
```

También puedes hacer un `git push` para que GitHub Actions los ejecute remotamente.
