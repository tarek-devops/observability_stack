# Observability Stack & Azure DevOps Assignment

This directory contains example files to help you prepare for the live assignments:

- **Kubernetes Observability Stack**: Deploy Prometheus, Grafana, and OpenTelemetry Collector.
- **Azure DevOps Pipeline**: Example pipeline for both Linux (bash) and Windows (PowerShell).

---

## Structure

- `k8s/` - Kubernetes manifests for Prometheus, Grafana, and OpenTelemetry Collector
- `azure-pipelines/` - Example Azure DevOps pipeline YAMLs
- `README.md` - This file

---

# How to Set Up and Test on Azure AKS

## Create an AKS Cluster

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Login to Azure:
   ```bash
   az login
   az login --use-device-code
   az account show
   az account list --output table
   az account list --refresh
   az provider list --output table

   ```

3. Create a resource group:
   ```bash
   az group create --name rg-k8s-practice --location swedencentral

   # Optional
   az provider register --namespace Microsoft.OperationalInsights --subscription azure_free_sub
   az provider show --namespace Microsoft.Insights --query "registrationState"

   ```
   The Standard_B2s_v2 VM in Azure has 2 vCPUs, 8 GiB RAM, supports Premium SSDs, and uses burstable credits for CPU performance

4. Create AKS cluster:
   ```bash
   RESOURCE_GROUP="rg-k8s-practice"
   CLUSTER_NAME="observability-cluster"
   LOCATION="swedencentral"
   NODE_COUNT=2
   NODE_SIZE="Standard_B2s_v2 "

   az aks create \
   --resource-group $RESOURCE_GROUP \
   --name $CLUSTER_NAME \
   --node-count $NODE_COUNT \
   --node-vm-size $NODE_SIZE \
   --enable-managed-identity \
   --generate-ssh-keys \
   --network-plugin azure \
   --network-policy azure \
    --enable-addons monitoring
   ```
5. Get credentials for kubectl:
   ```bash
   az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
   ```

6. Get nodes
     ```bash
     
    kubectl get nodes -o wide
    >
      NAME                                STATUS   ROLES    AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
      aks-nodepool1-11079928-vmss000000   Ready    <none>   26h   v1.33.5   10.224.0.33   <none>        Ubuntu 22.04.5 LTS   5.15.0-1099-azure   containerd://1.7.29-1
      aks-nodepool1-11079928-vmss000001   Ready    <none>   26h   v1.33.5   10.224.0.4    <none>        Ubuntu 22.04.5 LTS   5.15.0-1099-azure   containerd://1.7.29-1
    kubectl cluster-info
    >
      Kubernetes control plane is running at https://observabil-rg-k8s-practice-f6b1d4-2llhmr90.hcp.swedencentral.azmk8s.io:443
      CoreDNS is running at https://observabil-rg-k8s-practice-f6b1d4-2llhmr90.hcp.swedencentral.azmk8s.io:443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
      Metrics-server is running at https://observabil-rg-k8s-practice-f6b1d4-2llhmr90.hcp.swedencentral.azmk8s.io:443/api/v1/namespaces/kube-system/services/https:metrics-server:/proxy

      To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
    ```
-------------------------------------------

## Verify metrics are received by Otel collector
```bash
kubectl logs deploy/otel-collector -n observability
# Add a debug container
kubectl debug pods/prometheus- -it --image=busybox --target=<container-name>

kubectl debug -n observability pods/prometheus-778588f7bf-ltrvt -it \
  --image=busybox \
  --target=prometheus \
  --profile=general
then
wget -qO- http://localhost:9090/-/healthy
wget -qO- http://localhost:8889/-/healthy

# check the port of first container is listen or not
netstat -tln | grep 8889
tcp        0      0 :::8889                 :::*                    LISTEN   
ps aux
PID   USER     TIME  COMMAND
    1 10001     0:11 /otelcol --config=/etc/otel-collector-config.yaml
   62 root      0:00 sh

# Get inside container
kubectl exec -it <pod-name> -c debug-container -- sh

# Copy namespace/pod_name:volumen_path
kubectl cp observability/otel-collector-5756646988-5nvsr:/etc/otel-collector-config.yaml ./otel-config.yaml

```
