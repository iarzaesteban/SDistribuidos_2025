# Estructura de despliegue para microservicios - Pilar 3.1

# Carpeta sugerida: pilar3/infra/deployments/

# Archivos por separado:
# - backend.yaml
# - coordinator.yaml
# - frontend.yaml
# - split.yaml
# - joiner.yaml
# - pool.yaml
# - worker_mock.yaml
# - worker_real.yaml

# README.md - Despliegue con imágenes en Google Container Registry (GCR)

## 📁 Ubicación
Todos los archivos YAML están en `pilar3/infra/deployments/`.

## 🐳 Push de imágenes a GCR (PowerShell para Windows)
Usá el script `push_all.ps1` para:
- Buildear localmente todas las imágenes.
- Etiquetarlas con `gcr.io/blockchainsd2025/...`
- Subirlas a Google Container Registry.

📥 Descargá el script acá: [push_all.ps1](sandbox:/mnt/data/push_all.ps1)

Ejecutalo así desde PowerShell:
```powershell
./push_all.ps1
```

## ▶️ Orden de despliegue sugerido
1. `backend.yaml`
2. `coordinator.yaml`
3. `frontend.yaml`
4. `split.yaml`
5. `joiner.yaml`
6. `pool.yaml`
7. `worker_mock.yaml`
8. `worker_real.yaml` (si tenés nodos GPU en GKE)

Aplicá todos los manifiestos juntos con:
```powershell
kubectl apply -f ./pilar3/infra/deployments/
```

## ✅ Checklist de validación
- [ ] Todos los pods en estado `Running`.
- [ ] Servicios accesibles entre sí (`backend` → `coordinator`, `redis`, `rabbitmq`).
- [ ] `frontend` visible (usando `NodePort` o `LoadBalancer`).
- [ ] `worker_mock` y/o `worker_real` conectados y procesando.

---
📌 Reemplazá los nombres de imagen si cambiás el ID del proyecto o el repositorio de GCP.
