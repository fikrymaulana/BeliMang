# Deploying and Managing Apps to a Kubernetes Cluster

This tutorial describes everything you need to know about deploying and managing applications in the Project Sprint Kubernetes cluster.

## Prerequisites

Before deploying and managing apps in the Kubernetes cluster, you need to connect to it. For Project Sprint, you'll receive a kubeconfig file with the necessary configuration and credentials. Ensure you have the following:

1. **kubectl** installed on your machine (run `which kubectl` to check).
2. **kubeconfig** file provided by Project Sprint.

## Connecting to the Cluster

To connect to the cluster:

1. Load the kubeconfig file:

   ```bash
   export KUBECONFIG=/absolute/path/to/team_name.kubeconfig
   ```

2. Test the connection and account:

   ```bash
   kubectl auth whoami
   ```

   If you see the username and group, you're successfully connected. You can also follow [this guide](https://app.capacities.io/home/3409e60d-6aa3-48bb-92dd-349005a57b0c) to connect.

## Namespaces

Kubernetes uses namespaces to separate apps and resources.

1. To list all available namespaces:

   ```bash
   kubectl get namespaces
   # or
   kubectl get ns
   ```

2. To create a new namespace:

   ```bash
   kubectl create namespace <my-namespace>
   ```

3. To delete a namespace:

   ```bash
   kubectl delete namespace <my-namespace>
   ```

## Deployment

To deploy an app to a namespace, create the deployment configuration.

Before deploying, build and push the app image to an image registry.

- To push to the Project Sprint registry, follow [this link](https://app.capacities.io/home/40c66ced-659f-4ec6-a824-1fff32bd2754).
- To push to your GitHub account registry, follow the steps in [GHCR-README](k8/GHCR-README.md).

All resources for app deployments are in the `k8` folder. Follow the steps in [BeliMang Kubernetes Deployment](k8/README.md) to deploy the apps.

Modify the scripts to match your configurations, especially namespace, resources, and app-specific configs.

## Troubleshooting

### Checking Pod Status

After deployment, check pod status with:

```bash
kubectl get pods -n <my-namespace>
```

It should return something like:

```bash
NAME                           READY   STATUS    RESTARTS   AGE
belimang-app-c5766bf44-m2tzn   1/1     Running   0          43s
minio-6787fbcf8-j44ch          1/1     Running   0          7h31m
postgres-64f69b5d4-h9ddd       1/1     Running   0          7h31m
```

If any status is not "Running" or shows an error, check details and logs:

```bash
kubectl describe pod <pod-name> -n <my-namespace>
kubectl logs <pod-name> -n <my-namespace>
```

Example:

```bash
kubectl describe pod belimang-app-c5766bf44-m2tzn -n <my-namespace>
kubectl logs belimang-app-c5766bf44-m2tzn -n <my-namespace>
```

### Fixing Issues

If issues are identified and fixed, rebuild the app and redeploy by deleting the deployment and reapplying it to use the new image.

Delete the deployment:

```bash
kubectl delete deployment <deployment-name> -n <my-namespace>
```

Example:

```bash
kubectl delete deployment belimang-app -n <my-namespace>
```

Then redeploy:

```bash
kubectl apply -f <deployment-file>
```

Example:

```bash
kubectl apply -f app-deployment.yaml
```

### Other Commands

Useful commands for managing resources:

```bash
# Get all services with local IPs and ports
kubectl get svc -n <my-namespace>

# Delete a service
kubectl delete svc <service-name> -n <my-namespace>

# Get all resources in a namespace
kubectl get all -n <my-namespace>

# Delete all deployments in a namespace
kubectl delete deployment --all -n <my-namespace>