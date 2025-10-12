# BeliMang! Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the BeliMang! application with PostGIS and MinIO in the `snake-production` namespace.

## Architecture

The deployment consists of:

- **Application**: FastAPI-based marketplace application with 3 replicas (7 CPU cores, 21GB RAM per pod)
- **PostGIS**: PostgreSQL database with PostGIS extensions (version 15-3.3, 7 CPU cores, 21GB RAM)
- **MinIO**: Object storage server for file uploads (2 CPU cores, 4GB RAM)
- **Load Balancer**: External access to the application
- **Ingress**: Optional external access with custom domain (requires nginx ingress controller)

## Files

- `namespace.yaml` - Creates the belimang namespace
- `configmap.yaml` - Non-sensitive configuration
- `secret.yaml` - Sensitive data (credentials, keys)
- `pvc.yaml` - Persistent storage for PostGIS and MinIO
- `postgis-deployment.yaml` - PostGIS database deployment and service
- `minio-deployment.yaml` - MinIO server deployment and service
- `app-deployment.yaml` - Main application deployment with load balancer
- `ingress.yaml` - Optional ingress for custom domain access
- `Dockerfile` - Application container definition
- `deploy.sh` - Automated deployment script
- `README.md` - This documentation

## Prerequisites

1. **Kubernetes cluster** with sufficient resources
2. **kubectl** configured to access your cluster
3. **Docker** for building the application image
4. **nginx ingress controller** (optional, for ingress functionality)

## Dependencies

The application uses `psycopg2-binary` for PostgreSQL connectivity, which is optimized for container deployments and doesn't require PostgreSQL development headers.

## Deployment

1. **Build and deploy everything:**

```bash
# Apply in order
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f pvc.yaml
kubectl apply -f postgis-deployment.yaml
kubectl apply -f minio-deployment.yaml
kubectl apply -f app-deployment.yaml

```

2. **Check deployment status:**
   ```bash
   kubectl get pods -n snake-production
   kubectl get services -n snake-production
   ```

3. **Get the load balancer IP:**
   ```bash
   kubectl get services belimang-app-loadbalancer -n belimang
   ```

## Configuration

### Update for Production

1. **Change default passwords** in `secret.yaml`:
   - Update POSTGRES_USER and POSTGRES_PASSWORD
   - Update MINIO_ACCESS_KEY and MINIO_SECRET_KEY
   - Generate a new SECRET_KEY for JWT

2. **Update domain** in `ingress.yaml`:
   ```yaml
   rules:
   - host: your-actual-domain.com
   ```

3. **Storage sizing** in `pvc.yaml`:
   - Adjust storage sizes based on your needs

### Environment Variables

The application uses these environment variables:

| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Constructed | PostgreSQL connection string |
| MINIO_ENDPOINT | ConfigMap | MinIO server endpoint |
| MINIO_ACCESS_KEY | Secret | MinIO access key |
| MINIO_SECRET_KEY | Secret | MinIO secret key |
| MINIO_BUCKET | ConfigMap | Default bucket name |
| SECRET_KEY | Secret | JWT signing key |

## Services

| Service | Port | Type | Description |
|---------|------|------|-------------|
| belimang-app-loadbalancer | 80, 443 | LoadBalancer | External app access (7 CPU, 21GB RAM) |
| belimang-app-service | 8000 | ClusterIP | Internal app access (7 CPU, 21GB RAM) |
| postgres-service | 5432 | ClusterIP | Database access (7 CPU, 21GB RAM) |
| minio-service | 9000, 9001 | ClusterIP | MinIO API and console (2 CPU, 4GB RAM) |

## Scaling

Scale the application:
```bash
kubectl scale deployment belimang-app --replicas=5 -n snake-production
```

## Troubleshooting

1. **Check pod logs:**
   ```bash
   kubectl logs -l app=belimang-app -n snake-production
   ```

2. **Check service status:**
   ```bash
   kubectl describe service belimang-app-loadbalancer -n snake-production
   ```

3. **Check persistent volumes:**
   ```bash
   kubectl get pvc -n snake-production
   kubectl describe pvc postgres-pvc minio-pvc -n snake-production
   ```

## Database Migrations

The application runs database migrations automatically on startup. If you need to run them manually:

```bash
kubectl exec -it deployment/belimang-app -n belimang -- alembic upgrade head
```

## Backup and Recovery

### PostGIS Backup
```bash
kubectl exec deployment/postgres -n snake-production -- pg_dump -U snakeoadmin belimang > backup.sql
```

### MinIO Backup
```bash
kubectl exec deployment/minio -n snake-production -- mc alias set local http://localhost:9000 minioadmin minioadmin123
kubectl exec deployment/minio -n snake-production -- mc cp --recursive local/uploads /backup
```

## Security Notes

- Change all default passwords before production use
- Use proper RBAC for service accounts
- Enable TLS/SSL for production traffic
- Regularly update container images
- Monitor resource usage and logs

## Support

For issues with the Kubernetes deployment:
1. Check the logs of all pods
2. Verify resource limits and requests
3. Ensure persistent volumes are properly bound
4. Check network policies if applicable