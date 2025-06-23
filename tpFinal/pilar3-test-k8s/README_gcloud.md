# 📘 Guía rápida para pruebas en Kubernetes + Envío de transacciones

Este README contiene los comandos útiles para interactuar con el sistema blockchain desplegado en GKE, incluyendo cómo enviar transacciones y cómo reiniciar componentes relevantes.

---

## 🚀 Enviar una transacción

Desde la carpeta `tpFinal\Pilar2\client`, corré el siguiente comando:

```bash
python client_prefix_gcloud.py
```

Este script enviará una transacción al Coordinador en GCloud. Asegurate de tener configurado correctamente el `.env` con la URL del coordinador y los parámetros necesarios.

---

## 🚀 Enviar tareas al coordinador

Desde la carpeta `tpFinal\Pilar2\client`, corré el siguiente comando:

```bash
python3 stress_test.py
```

Este script enviará una o la cantidad de tarees que le indiques al Coordinador en GCloud. Asegurate de tener configurado correctamente el `.env` con la URL del coordinador y los parámetros necesarios.

---

## 🔎 Ver estado de los pods

```bash
kubectl get pods -n pilar3-test
```

---

## 🔁 Reiniciar componentes

Podés reiniciar cualquier deployment con este comando:

```bash
kubectl rollout restart deployment <nombre-del-deployment> -n pilar3-test
```

Ejemplos comunes:

```bash
kubectl rollout restart deployment nct -n pilar3-test
kubectl rollout restart deployment pool -n pilar3-test
kubectl rollout restart deployment validator -n pilar3-test
kubectl rollout restart deployment worker-mock-1 -n pilar3-test
kubectl rollout restart deployment worker-mock-2 -n pilar3-test
kubectl rollout restart deployment worker-mock-3 -n pilar3-test
kubectl rollout restart deployment frontend -n pilar3-test
kubectl rollout restart deployment mover -n pilar3-test
```

---

## 📜 Ver logs de un pod

```bash
kubectl logs <nombre-del-pod> -n pilar3-test
```

Para seguir logs en tiempo real:

```bash
kubectl logs -f <nombre-del-pod> -n pilar3-test
```

## Ver ip del front

```bash
kubectl get svc frontend -n pilar3-test
```

---

## 🧹 Limpiar Redis (vaciar blockchain)

```bash
kubectl exec -n pilar3-test -it redis-697469f66b-88zzh -- redis-cli -a thebestpassever FLUSHALL
kubectl exec -n pilar3-test -it redis-697469f66b-jx2z6 -- redis-cli -a thebestpassever FLUSHALL
```

---

## 🐇 Purgar colas de RabbitMQ (opcional)

Listar colas:

```bash
kubectl exec -n pilar3-test -it rabbitmq-78d7699586-lv6lk -- rabbitmqctl list_queues
```

Purgar una cola (por ejemplo, `mining_tasks`):

```bash
kubectl exec -n pilar3-test -it rabbitmq-78d7699586-lv6lk -- rabbitmqctl purge_queue mining_tasks
```

---

## 🧠 

- Si hacés cambios en los archivos `.yaml`, usá `kubectl apply` para actualizarlos.
- Podés monitorear recursos con `kubectl top pods -n pilar3-test` (si tenés `metrics-server` instalado).

---