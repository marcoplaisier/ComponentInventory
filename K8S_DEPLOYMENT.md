# K3s Deployment Guide

This guide explains how to deploy the Component Inventory application on K3s (lightweight Kubernetes).

## Prerequisites

- K3s installed and running
- kubectl configured to access your K3s cluster

## Quick Start

The application is automatically built and published to GitHub Container Registry (GHCR) via GitHub Actions on every push to the main branch.

### 1. Pull from GitHub Container Registry (Recommended)

The deployment manifest is pre-configured to use images from GHCR:

```bash
# For public repositories, the image will be pulled automatically
# For private repositories, create an image pull secret:
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-token> \
  --docker-email=<email> \
  -n component-inventory

# Then add imagePullSecrets to deployment.yaml:
# spec:
#   template:
#     spec:
#       imagePullSecrets:
#       - name: ghcr-secret
```

### 2. Deploy to K3s

Deploy all resources using kubectl:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or using kustomize
kubectl apply -k k8s/
```

## Alternative: Build Locally

If you prefer to build the image locally instead of using GHCR:

```bash
# Build the Docker image
docker build -t component-inventory:latest .

# Option A: Import into K3s containerd
docker save component-inventory:latest -o component-inventory.tar
sudo k3s ctr images import component-inventory.tar

# Option B: Use a local registry
docker tag component-inventory:latest localhost:5000/component-inventory:latest
docker push localhost:5000/component-inventory:latest

# Update deployment.yaml to use local image:
# image: component-inventory:latest  # or localhost:5000/component-inventory:latest
# imagePullPolicy: IfNotPresent
```

### 3. Verify Deployment

Check that all resources are running:

```bash
# Check namespace
kubectl get namespaces

# Check all resources in the namespace
kubectl get all -n component-inventory

# Check persistent volume claim
kubectl get pvc -n component-inventory

# Check pod logs
kubectl logs -n component-inventory -l app=component-inventory
```

### 4. Access the Application

Get the LoadBalancer IP or use port-forwarding:

```bash
# Check service status
kubectl get svc -n component-inventory

# For K3s, the LoadBalancer IP will be your node IP
# Access the application at http://<NODE_IP>:80

# Or use port-forward for local testing
kubectl port-forward -n component-inventory svc/component-inventory 8080:80

# Then access at http://localhost:8080
```

## Architecture

The deployment consists of:

- **Namespace**: `component-inventory` - Isolated namespace for the application
- **Deployment**: Single replica (can be scaled) running the Flask application
- **Service**: LoadBalancer service exposing the application on port 80
- **PersistentVolumeClaim**: 1Gi volume for SQLite database persistence
- **GitHub Actions**: Automated CI/CD pipeline for building and publishing container images

## Configuration

### Environment Variables

The application supports the following environment variables (configured in `deployment.yaml`):

- `DATABASE_PATH`: SQLite database file path (default: `sqlite:////data/components.db`)
- `FLASK_DEBUG`: Enable debug mode (default: `false`)

### Resource Limits

Default resource configuration:

- Requests: 100m CPU, 128Mi memory
- Limits: 500m CPU, 256Mi memory

Adjust these in `k8s/deployment.yaml` based on your workload.

### Storage

The deployment uses K3s's default `local-path` storage class. The database is persisted in a 1Gi PersistentVolume.

To use a different storage class, modify `storageClassName` in `k8s/pvc.yaml`.

## Scaling

Scale the deployment replicas:

```bash
kubectl scale deployment component-inventory -n component-inventory --replicas=3
```

**Note**: Since this uses SQLite, scaling beyond 1 replica may cause database locking issues. For production with multiple replicas, consider migrating to PostgreSQL or MySQL.

## Updating the Application

### Automated Updates (GHCR)

When using GHCR, updates are automatic:

```bash
# 1. Push changes to main branch or create a version tag
git tag v1.1.0
git push origin v1.1.0

# 2. GitHub Actions will build and push the new image automatically

# 3. Restart the deployment to pull the new image
kubectl rollout restart deployment/component-inventory -n component-inventory

# 4. Monitor the rollout
kubectl rollout status deployment/component-inventory -n component-inventory
```

### Manual Updates (Local Build)

If building locally:

```bash
# Build new image with a version tag
docker build -t component-inventory:v1.1 .

# Import into K3s
docker save component-inventory:v1.1 -o component-inventory.tar
sudo k3s ctr images import component-inventory.tar

# Update the deployment
kubectl set image deployment/component-inventory \
  component-inventory=component-inventory:v1.1 \
  -n component-inventory

# Or edit deployment.yaml and reapply
kubectl apply -f k8s/deployment.yaml
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n component-inventory
kubectl describe pod <pod-name> -n component-inventory
kubectl logs <pod-name> -n component-inventory
```

### Check PVC Status

```bash
kubectl get pvc -n component-inventory
kubectl describe pvc component-inventory-pvc -n component-inventory
```

### Common Issues

1. **Image Pull Issues**:
   - For GHCR: Check if the repository is private and requires authentication
     ```bash
     kubectl describe pod <pod-name> -n component-inventory
     kubectl get events -n component-inventory
     ```
   - For local images: Ensure the image is available in K3s's containerd
     ```bash
     sudo k3s crictl images | grep component-inventory
     ```

2. **Database Permissions**: Check that the pod has write access to the volume
   ```bash
   kubectl exec -n component-inventory <pod-name> -- ls -la /data
   ```

3. **Service Not Accessible**: Verify the LoadBalancer service has an external IP
   ```bash
   kubectl get svc -n component-inventory
   ```

4. **GHCR Authentication**: For private repositories, ensure image pull secret is configured
   ```bash
   kubectl get secrets -n component-inventory
   kubectl describe secret ghcr-secret -n component-inventory
   ```

## Uninstalling

Remove all resources:

```bash
# Delete all resources
kubectl delete -f k8s/

# Or using kustomize
kubectl delete -k k8s/

# Verify deletion
kubectl get all -n component-inventory
```

## Production Considerations

For production deployments:

1. **Database**: Migrate from SQLite to a proper database (PostgreSQL, MySQL)
2. **Secrets**: Use Kubernetes Secrets for sensitive configuration
3. **Ingress**: Configure an Ingress controller instead of LoadBalancer
4. **TLS**: Add TLS/SSL certificates for HTTPS
5. **Monitoring**: Add Prometheus metrics and monitoring
6. **Backups**: Implement database backup strategy
7. **Health Checks**: Fine-tune liveness and readiness probes
8. **Resource Limits**: Adjust based on actual usage patterns

## Example API Calls

Once deployed, test the API:

```bash
# Get the service URL
SERVICE_URL=$(kubectl get svc component-inventory -n component-inventory -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create a component
curl -X POST http://${SERVICE_URL}/components \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arduino Uno",
    "type": "Microcontroller",
    "version": "R3",
    "description": "ATmega328P based microcontroller board",
    "amount": 5,
    "datasheet_url": "https://example.com/arduino-uno.pdf"
  }'

# List all components
curl http://${SERVICE_URL}/components
```
