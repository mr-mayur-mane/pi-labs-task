# Task Management Application on Kubernetes

A simple Task Management application deployed on a single-node Kubernetes cluster using Minikube, demonstrating core Kubernetes concepts including StatefulSets, persistent storage, node scheduling, and NGINX-based reverse proxying.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Namespace](#namespace)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Start Minikube](#1-start-minikube)
  - [2. Label the Kubernetes Node](#2-label-the-kubernetes-node)
  - [3. Build Application Images](#3-build-application-images)
  - [4. Deploy Kubernetes Resources](#4-deploy-kubernetes-resources)
  - [5. Verify Deployment](#5-verify-deployment)
- [Persistent Storage](#persistent-storage)
- [NGINX Reverse Proxy](#nginx-reverse-proxy)
- [Path-Based Routing](#path-based-routing)
- [Validating Data Persistence](#validating-data-persistence)
- [What This Project Demonstrates](#what-this-project-demonstrates)

## Overview

This project runs a Task Management app on a single-node Kubernetes cluster (Minikube, Docker driver) on Windows 11.

**Components:**

- Frontend application
- Flask backend API
- PostgreSQL database using a `StatefulSet`
- Persistent storage via `PVC` / `PV`, using Minikube's default **`standard`** `StorageClass`
- Node scheduling using `nodeSelector`
- NGINX reverse proxy with path-based routing
- Kubernetes `ConfigMap` and `Secret`
- Namespace isolation

## Architecture

```text
Windows 11
    │
Docker Desktop
    │
Minikube (single-node cluster)
    │
NodePort
    │
  NGINX
    │
    ├──── /app ────► Frontend Service
    │
    └──── /api ────► Backend Service
                          │
                          ▼
                    PostgreSQL StatefulSet
                          │
                          ▼
                         PVC ──► PV ──► StorageClass (standard)
```

**Request flow:**

```text
Browser
   │
   ▼
NGINX (NodePort)
   │
   ├── /app/ ──► Frontend Service
   │
   └── /api/ ──► Backend Service
                     │
                     ▼
                 PostgreSQL
```

> NGINX is deployed directly as a reverse proxy. Kubernetes Ingress is **not** used.

## Namespace

All resources are deployed into the `task-app` namespace:

```bash
kubectl apply -f k8s/namespace.yaml
```

## Project Structure

```text
pi-labs-task/
│
├── app/
│   ├── backend/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/
│       ├── index.html
│       └── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── nginx-configmap.yaml
│   ├── nginx-deployment.yaml
│   └── nginx-service.yaml
│
└── README.md
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

Verify installation:

```bash
docker --version
minikube version
kubectl version --client
```

## Getting Started

### 1. Start Minikube

```bash
minikube start --driver=docker
```

Verify the cluster:

```bash
kubectl get nodes
```

Expected output:

```text
NAME       STATUS   ROLES           AGE
minikube   Ready    control-plane   ...
```

Get the Minikube IP:

```bash
minikube ip
```

### 2. Label the Kubernetes Node

The PostgreSQL workload is scheduled using a node label.

```bash
kubectl label nodes minikube workload=database
```

Verify:

```bash
kubectl get nodes --show-labels
```

The node should show `workload=database`. The PostgreSQL `StatefulSet` uses:

```yaml
nodeSelector:
  workload: database
```

**Scheduling decision:** since this is a single-node cluster, the label ensures the database workload explicitly targets the node designated for database workloads — demonstrating Kubernetes node scheduling via `nodeSelector`.

### 3. Build Application Images

```bash
docker build --no-cache -t task-backend:1.1 ./app/backend
docker build --no-cache -t task-frontend:1.1 ./app/frontend
```

Load the images into Minikube:

```bash
minikube image load task-backend:1.1
minikube image load task-frontend:1.1
```

Verify:

```powershell
minikube image ls | Select-String "task-"
```

### 4. Deploy Kubernetes Resources

Apply resources in the following order.

**Namespace**

```bash
kubectl apply -f k8s/namespace.yaml
```

**Secret and ConfigMap**

```bash
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
```

**PostgreSQL**

```bash
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
```

**Backend**

```bash
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/backend-deployment.yaml
```

**Frontend**

```bash
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

**NGINX**

```bash
kubectl apply -f k8s/nginx-configmap.yaml
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml
```

### 5. Verify Deployment

```bash
kubectl get all -n task-app
kubectl get pods -n task-app
```

Expected workloads: `backend`, `frontend`, `nginx`, `postgres-0` — all `Running`.

```bash
kubectl get svc -n task-app
```

## Persistent Storage

PostgreSQL uses a `StatefulSet` with a `PersistentVolumeClaim`, provisioned dynamically through Minikube's built-in **default `standard` StorageClass** (backed by the `k8s.io/minikube-hostpath` provisioner). No custom `StorageClass` was created for this project.

```bash
kubectl get pvc -n task-app
```

Expected:

```text
postgres-data-postgres-0   Bound
```

```bash
kubectl get storageclass
```

Expected — `standard` is marked as the default (via the `(default)` annotation):

```text
NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
standard (default)   k8s.io/minikube-hostpath   Delete          Immediate           false                  ...
```

```bash
kubectl get pv
```

`volumeClaimTemplates` used by the StatefulSet — `storageClassName` is set explicitly to `standard`:

```yaml
volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes:
        - ReadWriteOnce
      storageClassName: standard
      resources:
        requests:
          storage: 1Gi
```

The PVC is mounted inside PostgreSQL at `/var/lib/postgresql/data`.


## NGINX Reverse Proxy

NGINX is exposed via a Kubernetes `NodePort` Service.

```bash
kubectl get svc nginx -n task-app
minikube service nginx -n task-app --url
```

Example output:

```text
http://127.0.0.1:65308
```

> The port may change each time the Minikube service tunnel is recreated.

## Path-Based Routing

| Route   | Destination        |
|---------|---------------------|
| `/`     | Welcome page         |
| `/app/` | Frontend Service     |
| `/api/` | Backend Service      |

**Get tasks**

```text
GET http://127.0.0.1:<PORT>/api/tasks
```

**Create task**

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:<PORT>/api/tasks" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"Test Task"}'
```

**Delete task**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:<PORT>/api/tasks/1" -Method Delete
```
## Validating Data Persistence

Create a task:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:<PORT>/api/tasks" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"Persistent Task"}'
```

Verify the task exists:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:<PORT>/api/tasks" -Method Get
```

Delete the PostgreSQL pod:

```bash
kubectl delete pod postgres-0 -n task-app
```

Wait for it to be recreated:

```bash
kubectl get pods -n task-app -w
```

Once `postgres-0` is running again, verify the task again:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:<PORT>/api/tasks" -Method Get
```

The previously created task should still exist — confirming PostgreSQL data is stored on persistent storage rather than in the pod filesystem.

## What This Project Demonstrates

- [x] Kubernetes single-node cluster
- [x] Namespace isolation
- [x] Frontend deployment
- [x] Backend deployment
- [x] PostgreSQL StatefulSet
- [x] PersistentVolumeClaim / PersistentVolume using default `standard` StorageClass
- [x] Node labeling and `nodeSelector` scheduling
- [x] NGINX reverse proxy with path-based routing
- [x] Frontend ↔ backend ↔ PostgreSQL communication
- [x] Task creation, listing, and deletion
- [x] PostgreSQL data persistence after pod recreation