
# Pilar 3 – Estructura de archivos y directorios

> Este README resume **qué hay** en la carpeta `Pilar3/` y **para qué sirve** cada archivo.  

---

## Mapa de directorios detallado

```text
Pilar3/
├── README.md               ← mini‑guía del pilar (borrador que vas leyendo ahora)
│
├── coordinador/            ← microservicio “NCT” que reparte trabajo y valida bloques
│   ├── app/
│   │   ├── __init__.py     ← inicializa el paquete FastAPI
│   │   ├── main.py         ← arranca el servidor y gestiona startup / shutdown
│   │   ├── routes.py       ← define endpoints /mine, /blockchain, /heartbeat
│   │   └── heartbeat.py    ← helper para enviar heartbeats (TTL en Redis)
│   │
│   ├── utils/
│   │   └── helper.py       ← funciones comunes: logging, parseos, helpers varios
│   │
│   └── deploy/
│       ├── Dockerfile      ← build de la imagen del coordinador
│       └── requirements.txt← dependencias Python del coordinador
│
├── worker/                 ← minero GPU (CUDA) real
│   ├── main.cu             ← kernel CUDA que prueba hashes en paralelo
│   ├── md5.cu              ← implementación MD5 usada por el kernel
│   ├── md5.cuh             ← header de la lib MD5
│   ├── config.h            ← defines: prefijo objetivo, tamaño del batch, etc.
│   ├── worker.py           ← wrapper Python: consume tarea, llama kernel y publica resultado
│   ├── Dockerfile          ← imagen basada en nvidia/cuda:12.2‑runtime
│   └── requirements.txt    ← `pika`, `numpy` y libs auxiliares
│
└── infra/                  ← Infra as Code + manifests K8s que se aplican en GKE
    ├── main.tf                   ← crea el clúster GKE y los node‑pools (infra / app)
    ├── backend.tf                ← backend remoto GCS para el state de Terraform
    ├── variables.tf              ← variables de configuración (región, nombres, etc.)
    ├── versions.tf               ← lock de versiones de proveedores y Terraform
    ├── configmaps.tf             ← ConfigMaps con *redis.conf* y *rabbitmq.conf*
    ├── rabbitmq_stateful.tf      ← StatefulSet + PVC para RabbitMQ
    ├── storage.tf                ← StorageClass SSD zonal + plantilla de PVC
    ├── storage_and_secrets.tf    ← External‑Secrets / Vault (pendiente de pulir)
    ├── k8s_manifests.tf          ← aplica los YAML de /deployments y /services con `kubectl`
    ├── output.tf                 ← expone IPs, nombres de nodo y otros outputs útiles
    ├── hpa.yaml                  ← ejemplo de HPA para *worker_mock* (comentado)
    │
    ├── deployments/              ← Deployments & StatefulSets fuente‑de‑verdad
    │   ├── backend.yaml          ← Deployment del microservicio Backend (FastAPI)
    │   ├── coordinator.yaml      ← Deployment del Coordinador (NCT)
    │   ├── frontend.yaml         ← Deployment del Frontend (React/Vite)
    │   ├── joiner.yaml           ← Deployment que unifica resultados de split
    │   ├── pool.yaml             ← Deployment del pool de transacciones
    │   ├── split.yaml            ← Deployment que parte imágenes/inputs en N trozos
    │   ├── worker_mock.yaml      ← Deployment de workers fake (CPU) para tests locales
    │   ├── worker_real.yaml      ← Deployment de worker GPU real (usa node‑selector nvidia)
    │   └── worker-mock-hpa.yaml  ← HPA que escala *worker_mock* según CPU
    │
    ├── services/                 ← Services que exponen pods dentro/fuera del clúster
    │   ├── backend_service.yaml      ← ClusterIP + NodePort opcional para Backend
    │   ├── coordinator_service.yaml  ← NodePort para Coordinador (puerto 11111)
    │   ├── frontend_service.yaml     ← LoadBalancer (Angular/React) público
    │   ├── joiner_service.yaml       ← ClusterIP para Joiner
    │   ├── split_service.yaml        ← ClusterIP para Split
    │   └── worker-mock_service.yaml  ← ClusterIP para Worker Mock
    │
    ├── patch-metrics.json        ← parche RBAC que habilita `metrics-server`
    ├── Makefile                  ← atajos: `make apply`, `make destroy`, etc.
    ├── deployments/
    │   └── deploy_all.ps1        ← script PowerShell de despliegue rápido (`kubectl apply -f`)
    │
    └── secrets/                  ← git‑ignored: SA key de GCP y variables `.env`
```

---

## ¿Para qué sirve cada bloque?

| Bloque | Rol dentro del Pilar 3 |
|--------|------------------------|
| **coordinador/** | Orquesta el minado: publica tareas en RabbitMQ, valida resultados y guarda bloques en Redis. También gestiona heartbeats de workers. |
| **worker/** | Minero GPU real (CUDA). Aprovecha GPUs T4 en GKE para acelerar el cómputo de hashes. |
| **infra/*.tf** | Infra as Code con OpenTofu: clúster GKE, node‑pools, StorageClasses, ConfigMaps, Secrets y aplicación de manifests. |
| **infra/deployments/** | YAMLs fuente de Deployments y StatefulSets para cada microservicio y base de datos. |
| **infra/services/** | YAMLs de Services que exponen los pods y permiten descubrimiento por DNS. |
| **patch-metrics.json** | Parche para que el metrics‑server tenga permiso de leer CPU/memoria y el HPA funcione. |
| **Makefile & deploy_all.ps1** | Atajos CLI: `make` para Terraform y script PowerShell en una sola línea para aplicar manifests. |
| **secrets/** | Carpeta excluida del control de versiones que guarda claves y variables sensibles. |

---