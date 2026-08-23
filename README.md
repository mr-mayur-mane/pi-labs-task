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
- [Validating Data Persistence](#validating-data-persistence)
- [NGINX Reverse Proxy](#nginx-reverse-proxy)
- [Path-Based Routing](#path-based-routing)
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
│   ├──