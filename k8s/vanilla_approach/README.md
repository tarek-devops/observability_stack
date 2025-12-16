# Observability Stack Example (Vanilla Approach)

This folder contains:
- Kubernetes manifests for deploying:
  - Prometheus
  - Grafana
  - OpenTelemetry Collector
- Other files:
  - README.md
  - vanilla_approach_definition.md

---

## Create the Observability Namespace

```bash
cd k8s
kubectl create namespace observability
kubectl config set-context --current --namespace=observability
```

---

## Deploy Prometheus, Grafana, and OpenTelemetry Collector
### option A: Service Type: ClusterIP for otel, Grafana , Prometheus
1. Set service type: ClusterIP then Apply all manifests in the `k8s/` folder:
```bash
kubectl apply -f k8s/otel-collector-config.yaml
kubectl apply -f k8s/otel-collector-deployment.yaml
kubectl apply -f k8s/prometheus-config.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-config.yaml
kubectl apply -f k8s/grafana-deployment.yaml

# Port-forward for local access
kubectl -n observability port-forward deploy/prometheus 9090:9090 &
kubectl -n observability port-forward deploy/grafana 3000:3000 &
kubectl -n observability port-forward deploy/otel-collector 4318:4318 &
```

2. Set this in `simple-metrics-sender.py`:
```python
endpoint = os.getenv("OTEL_ENDPOINT", "http://localhost:4318/v1/metrics")
```

Access UIs:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
(No UI for Otel)

#### How to Test
1. Run the metrics sender and check Prometheus:
   ```bash
   python metrics-app/simple-metrics-sender.py
   📊 [00:29:57] Sent metrics: requests=304, duration=0.514s
   📊 [00:29:59] Sent metrics: requests=305, duration=0.598s
   📊 [00:30:00] Sent metrics: requests=306, duration=0.419s
   📊 [00:30:02] Sent metrics: requests=307, duration=0.175s
   📊 [00:30:04] Sent metrics: requests=308, duration=0.385s
   ```
2. In Prometheus UI, run query: `http_requests_total`
3. In Grafana, login (admin/admin), 
in grafana-config.yaml set url: `http://prometheus:9090` or `http://prometheus.observability.svc.cluster.local:9090`
go to Connections > Data sources > Prometheus > Test connection
then 
Explore > Prometheus, and query: `http_requests_total`

---

### Option B: LoadBalancer for Grafana & Otel, ClusterIP for Prometheus

Both Grafana and Otel-Collector get their own public IPs (costly, not recommended for production):

```bash
kubectl get services -n observability
# Example output:
# grafana          LoadBalancer   ...   135.225.7.29   3000:32000/TCP
# otel-collector   LoadBalancer   ...   9.223.17.201   4317:32579/TCP,4318:31761/TCP,8889:32334/TCP
# prometheus       ClusterIP      ...   <none>         9090/TCP
```
Port-forward Prometheus if needed:
```bash
kubectl -n observability port-forward deploy/prometheus 9090:9090 &
```

---

### Option C: ClusterIP for All, Expose via Ingress

All services share the same public IP via an ingress controller `(4.165.21.58)`   (recommended for production):

`<loadbalancer_public_IP>/grafana`  
`<loadbalancer_public_IP>/prometheus`  
`<loadbalancer_public_IP>/collector/v1/metrics`  
1. Set service type: ClusterIP for all services.
2. Add to Prometheus deployment:
   ```yaml
   - '--web.external-url=http://<DNS>/prometheus'
   - '--web.route-prefix=/'
   ```
3. Add to Grafana deployment:
   ```yaml
   env:
   - name: GF_SERVER_ROOT_URL
     value: "http://<DNS>/grafana"
   - name: GF_SERVER_SERVE_FROM_SUB_PATH
     value: "true"
   ```
4. Set DNS name label in Azure Portal for the public IP (e.g., demo123).  
`Azure Portal: Go to Public IP addresses → select your IP → Settings > Configuration then set DNS name label as demo123`  
So the DNS name is demo123.swedencentral.cloudapp.azure.com
http://demo123.swedencentral.cloudapp.azure.com/

5. Install NGINX ingress controller:
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
   --namespace ingress-nginx \
   --create-namespace \
   --set controller.service.type=LoadBalancer \
   --set controller.service.annotations."service.beta.kubernetes.io/azure-load-balancer-health-probe-request-path"=/healthz
```

```bash
kubectl get svc -n ingress-nginx
   NAME                                 TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
   ingress-nginx-controller    LoadBalancer   10.0.104.106   4.165.21.58   80:31479/TCP,443:30332/TCP   8h
   ingress-nginx-controller-admission  ClusterIP  10.0.216.200   <none>  443/TCP                      8h

kubectl get svc -n observability
   NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
   grafana          ClusterIP   10.0.127.50    <none>        3000/TCP                    
   otel-collector   ClusterIP   10.0.104.236   <none>        4317/TCP,4318/TCP,8889/TCP   
   prometheus       ClusterIP   10.0.120.137   <none>        9090/TCP                     8h
```

6. in Azure portal, Find Network security group of the worker node  
`Azure > VSG >  aks-agentpool-21673438-nsg > Settings > Inbound Security Rules`  
you will see a rule that allows connection to internet  
`500 k8s-azure-lb_allow_IPv4_556f7044ec033 port:443,80`  
`source: internet     Destination: 4.165.21.58`

7. Deploy the ingress manifest:
   ```bash
   kubectl apply -f k8s/observability-ingress-separate.yaml
   kubectl get ingress -A
   >
   NAMESPACE       NAME                 CLASS   HOSTS                                      ADDRESS       PORTS   AGE
   observability   grafana-ingress      nginx   demo123.swedencentral.cloudapp.azure.com   4.165.21.58   80      80m
   observability   otel-ingress         nginx   demo123.swedencentral.cloudapp.azure.com   4.165.21.58   80      80m
   observability   prometheus-ingress   nginx   demo123.swedencentral.cloudapp.azure.com   4.165.21.58   80      80m
   # Check for DNS and public IP
   ```
7. Set this in `simple-metrics-sender.py`:
   ```python
   endpoint = os.getenv("OTEL_ENDPOINT", "http://<DNS>/collector/v1/metrics")
   ```

#### How to Test
 1. Run the metrics sender 
 2. check otel page will show the following to indicate otel is working properly.
   `http://demo123.swedencentral.cloudapp.azure.com/collector/v1/metrics`  

   `405 method not allowed, supported: [POST]`
 3. check Prometheus and Grafana as above, but use the DNS URLs:
   - Prometheus: http://<DNS>/prometheus http://demo123.swedencentral.cloudapp.azure.com/prometheus
   - Grafana: http://<DNS>/grafana  http://demo123.swedencentral.cloudapp.azure.com/grafana/
      Login: admin / admin
   in grafana-config.yaml set url: `http://demo123.swedencentral.cloudapp.azure.com`
   go to Connections > Data sources > Prometheus > Test connection
   then 
   Explore > Prometheus, and query: `http_requests_total`

---

## Additional Azure/Aks/Ingress Notes

- Use `kubectl get svc -n ingress-nginx` and `kubectl get ingress -A` to verify public IP and DNS.
- For troubleshooting, use `kubectl logs`, `kubectl describe`, and `kubectl exec` as needed.

---

## See Also
- [vanilla_approach_definition.md](./vanilla_approach_definition.md) for a definition and pros/cons of the vanilla approach.