# Observability Stack Example (Operators Approach)

This folder contains Kubernetes custom resources for deploying:
- Prometheus (via Prometheus Operator)
- Grafana (via Grafana Operator)
- OpenTelemetry Collector (via OpenTelemetry Operator)
- Ingress for unified access

## Prerequisites
- install cert-manager (required for webhook TLS)
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

kubectl get pods -n cert-manager
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-7b8b89f89d-tcm8w              1/1     Running   0          2m6s
cert-manager-cainjector-7f9fdd5dd5-r947r   1/1     Running   0          2m6s
cert-manager-webhook-769f6b94cb-nclrh      1/1     Running   0          2m6s
```
- Namespace `observability` should exist.
- **Install the following operators in your cluster before applying the custom resources:**
  - Prometheus Operator
  - Grafana Operator
  - OpenTelemetry Operator

### Install Operators (Quick Start)

> **Note:** You only need to install each operator once per cluster. See official docs for advanced options and latest versions.


#### 1. Prometheus Operator
Installs Prometheus Operator with correct CRD.

The below helm command will install:
1. Prometheus Operator (for managing Prometheus, Alertmanager, ServiceMonitor, etc.)
2. Prometheus (metrics collection)
3. Grafana (the dashboard app, but not the operator)
4. Alertmanager
5. Node Exporter, Kube State Metrics, etc.
```bash

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade -i kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace observability --create-namespace

kubectl get all -n observability -l app.kubernetes.io/instance=kube-prometheus-stack

kubectl get all,configmap,secret,servicemonitor,podmonitor,prometheusrule,ingress -n observability -l app.kubernetes.io/instance=kube-prometheus-stack

# List All Resources Managed by Helm
kubectl get all --all-namespaces -l app.kubernetes.io/managed-by=Helm
```

#### 2. Grafana Operator
This installs the Grafana Operator, which reconciles CRDs like Grafana, GrafanaDatasource, GrafanaDashboard.
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade -i grafana-operator grafana/grafana-operator \
    --namespace observability --create-namespace 

```

#### 3. OpenTelemetry Operator
```bash
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
# Verify the secret and pod status:
kubectl get secret -n opentelemetry-operator-system
NAME                                                     TYPE                DATA   AGE
opentelemetry-operator-controller-manager-service-cert   kubernetes.io/tls   3      119s

kubectl get pods -n opentelemetry-operator-system
NAME                                                         READY   STATUS    RESTARTS   AGE
opentelemetry-operator-controller-manager-5c7f669795-ngw7v   2/2     Running   0          2m7s


```

---

## Run and test

1. **Apply Custom Resources:**
```bash
kubectl apply -f prometheus-operator-cr.yaml
kubectl apply -f otel-operator-cr_case1.yaml
```
2. Run the script and see what metrics collected by otel collecter
`http://demo-gateway.swedencentral.cloudapp.azure.com/otel-metrics`

3. Install Grafana 
```bash
kubectl apply -f grafana-operator-cr.yaml
```

```bash
kubectl get pods -n cert-manager

```
