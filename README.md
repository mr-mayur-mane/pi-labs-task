# Task Management Application on Kubernetes

## 1. Overview

This project demonstrates deployment of a simple Task Management application on a single-node Kubernetes cluster using Minikube.

The application consists of:

- Frontend application
- Flask backend API
- PostgreSQL database
- Persistent storage using Kubernetes PVC/PV
- Custom StorageClass
- Node scheduling using `nodeSelector`
- NGINX reverse proxy
- Path-based routing using NGINX
- Kubernetes namespace for application isolation

The complete application is deployed locally using Minikube with the Docker driver on Windows 11.

---

# 2. Architecture

```text
                         Windows 11
                             |
                       Docker Desktop
                             |
                          Minikube
                      Single Kubernetes Node
                             |
                    NodePort / NGINX
                             |
                     http://127.0.0.1:<PORT>
                             |
                         +-------+
                         | NGINX |
                         +---+---+
                             |
                +------------+------------+
                |                         |
             /app/                      /api/
                |                         |
                v                         v
        +---------------+        +---------------+
        |   Frontend    |        |    Backend    |
        |    Service    |        |    Service    |
        +---------------+        +-------+-------+
                                          |
                                          |
                                          v
                                  +---------------+
                                  |  PostgreSQL   |
                                  |  StatefulSet  |
                                  +-------+-------+
                                          |
                                          v
                                  +---------------+
                                  |      PVC      |
                                  +-------+-------+
                                          |
                                          v
                                  +---------------+
                                  |      PV       |
                                  +-------+-------+
                                          |
                                          v
                                  +---------------+
                                  | task-storage  |
                                  | StorageClass  |
                                  +---------------+

                                  