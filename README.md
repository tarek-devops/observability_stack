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

## 1. Create an AKS Cluster

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
    kubectl get nodes
    kubectl cluster-info
    >
    Kubernetes control plane is running at https://aks-practi-rg-k8s-practice-f6b1d4-5jyxw8uy.hcp.swedencentral.azmk8s.io:443
    CoreDNS is running at https://aks-practi-rg-k8s-practice-f6b1d4-5jyxw8uy.hcp.swedencentral.azmk8s.io:443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
    Metrics-server is running at https://aks-practi-rg-k8s-practice-f6b1d4-5jyxw8uy.hcp.swedencentral.azmk8s.io:443/api/v1/namespaces/kube-system/services/https:metrics-server:/proxy
    ```
## 2. Create Namespace (if needed)
```bash
kubectl create namespace observability
kubectl config set-context --current --namespace=observability
```



## 3. Build Metrics Application
```bash
cd metrics-app
pip install -r requirements.txt

# Test directly
python simple-metrics-sender.py

# Build Windows .exe
pip install pyinstaller
pyinstaller --onefile --name metrics-sender simple-metrics-sender.py
# Output: dist/metrics-sender.exe
```

## 4. Deploy Prometheus, Grafana, and OpenTelemetry Collector
Apply all manifests in the `k8s/` folder:
```bash
kubectl apply -f k8s//otel-collector-config.yaml
kubectl apply -f k8s/otel-collector-deployment.yaml
kubectl apply -f k8s/prometheus-config.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-config
kubectl apply -f k8s/grafana-deployment.yaml 


OR
chmod +x deploy-stack.sh
./deploy-stack.sh

# Wait for external IPs
kubectl get svc -n observability -w
kubectl -n observability port-forward deploy/prometheus 9090:9090 &
kubectl -n observability port-forward deploy/grafana 3000:3000 &
kubectl -n observability port-forward deploy/otel-collector 4318:4318 &

```
Test Metrics Sending
```bash
# Get OTel Collector IP
export OTEL_IP=$(kubectl get svc otel-collector -n observability -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Set endpoint for HTTP (port 4318)
export OTEL_ENDPOINT=http://$OTEL_IP:4318/v1/metrics

# Run metrics app based on your platform
cd ../metrics-app
./metrics-sender.exe  # Windows
OR
./metrics-sender-linux  # Linux
OR
python simple-metrics-sender.py  # Any platform
```

## 5. Verify metrics are received by Otel collector
```
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

## 5.Verify in Grafana
```bash
# Get Grafana IP
kubectl get svc grafana -n observability

# Open in browser: http://<GRAFANA-IP>:3000
# Login: admin / admin
# Navigate to: Explore > Prometheus
# Query: http_requests_total
```

