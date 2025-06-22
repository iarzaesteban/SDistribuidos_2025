$ErrorActionPreference = 'Stop'
$project = "blockchainsd2025"
$services = @(
    @{ name = "redis";           path = "";                   image = "redis:7.2-alpine";             skipBuild = $true },
    @{ name = "rabbitmq";        path = "";                   image = "rabbitmq:3-management";        skipBuild = $true },
    @{ name = "nct";             path = "Pilar2/coordinador"; df = "deploy/Dockerfile" },
    @{ name = "mover";           path = "Pilar2/exchanger";   df = "deploy/Dockerfile" },
    @{ name = "validator";       path = "Pilar2/validator";   df = "deploy/Dockerfile" },
    @{ name = "pool";            path = "Pilar2/pool";        df = "deploy/Dockerfile" },
    @{ name = "worker-mock-1";   path = "Pilar2/worker_mock"; df = "deploy/Dockerfile" },
    @{ name = "worker-mock-2";   path = "Pilar2/worker_mock"; df = "deploy/Dockerfile" },
    @{ name = "worker-mock-3";   path = "Pilar2/worker_mock"; df = "deploy/Dockerfile" },
    @{ name = "worker-real";     path = "Pilar2/worker-real"; df = "Dockerfile" },
    @{ name = "frontend";        path = "pilar3-test-k8s/frontend"; df = "Dockerfile" }
)

Write-Host "🔐 Autenticando Docker con GCloud..."
gcloud auth configure-docker

foreach ($s in $services) {
    if ($s.skipBuild) {
        Write-Host "⏩ Skipping build for image: $($s.name) (usará imagen pública)"
        continue
    }

    $imageName = "gcr.io/$project/$($s.name):latest"
    Write-Host "`n📦 Procesando imagen: $($s.name)"
    docker build -t $s.name -f "$($s.path)/$($s.df)" "$($s.path)"
    docker tag $s.name $imageName
    docker push $imageName
}
