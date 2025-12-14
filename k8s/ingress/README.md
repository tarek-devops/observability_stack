# Observability Stack Example

This folder contains Kubernetes manifests for deploying:
- Prometheus
- Grafana
- OpenTelemetry Collector

## Usage

1. Apply all manifests:
   ```bash
   cd k8s
   kubectl apply -f .
   ```
2. Port-forward Grafana to access UI:
   ```bash
   kubectl port-forward svc/grafana 3000:3000
   ```
3. Port-forward Prometheus if needed:
   ```bash
   kubectl port-forward svc/prometheus 9090:9090
   ```
4. Port-forward OpenTelemetry Collector (if needed):
   ```bash
   kubectl port-forward svc/otel-collector 4317:4317
   ```

## Notes
- Update configs as needed for your environment.
- Use `kubectl get pods` to check status.

Install Nginx ingress controller for Azure
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update


helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz

kubectl get services -A


