# Observability Stack Example (Gateway API Approach)

This folder contains Gateway API resources to expose:
- Prometheus
- Grafana
- OpenTelemetry Collector

## Prerequisites
Required:

1. Install Gateway API CRDs.

2. Install a Gateway API implementation (controller).
- NGINX Gateway Fabric (from the NGINX Ingress team).
- Azure: Application Gateway Ingress Controller (AGIC).
- AWS Gateway API Controller
- Istio (uses Gateway API to configure Istio gateways).
- Traefik (supports Gateway API).
- Kong Gateway.
3. Ensure your GatewayClass.controllerName matches the controller.

- Namespace `observability` should exist
- **Prometheus, Grafana, and Otel Collector must be deployed in the `observability` namespace.**

---

## nstall Gateway API and NGINX Gateway Controller

### Install Gateway API CRDs
```bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/latest/download/standard-install.yaml

#Verify the installation:
kubectl get crds | grep gateway
```

### 2. Install NGINX Gateway Controller

This command installs nginx gateway controller and GatewayClass to map to that controller

`https://docs.nginx.com/nginx-gateway-fabric/install/helm/`
```bash
helm install ngf oci://ghcr.io/nginx/charts/nginx-gateway-fabric --create-namespace -n nginx-gateway
OR

kubectl apply -f https://github.com/nginxinc/nginx-gateway-fabric/releases/<latest_version>/download/deploy.yaml


kubectl get gatewayclass -A
NAME    CONTROLLER                                   ACCEPTED   AGE
nginx   gateway.nginx.org/nginx-gateway-controller   True       26s

kubectl describe  gatewayclass/nginx
Name:         nginx
Namespace:
Labels:  
              app.kubernetes.io/managed-by=Helm
              app.kubernetes.io/name=nginx-gateway-fabric
              helm.sh/chart=nginx-gateway-fabric-2.2.2
Annotations:  meta.helm.sh/release-name: ngf
              meta.helm.sh/release-namespace: nginx-gateway
Kind:         GatewayClass
Spec:
  Controller Name:  gateway.nginx.org/nginx-gateway-controller

 kubectl get all -n nginx-gateway
NAME                                            READY   STATUS    RESTARTS   AGE
pod/ngf-nginx-gateway-fabric-7d5b85c8b4-99q9r   1/1     Running   0          4m30s

NAME                               TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/ngf-nginx-gateway-fabric   ClusterIP   10.0.95.38   <none>        443/TCP   4m30s

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ngf-nginx-gateway-fabric   1/1     1            1           4m30s

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/ngf-nginx-gateway-fabric-7d5b85c8b4   1         1         1       4m30s
```
Set DNS name label in Azure Portal for the public IP (e.g., demo-gateway).  
`Azure Portal: Go to Public IP addresses → select your IP → Settings > Configuration then set DNS name label as demo-gateway`  
---

## 1. Deploy Prometheus, Grafana, and OpenTelemetry Collector

You can use the vanilla manifests or operator CRs from the other approach folders, or Helm charts. Example (vanilla YAML):

```bash
kubectl apply -f ../vanilla_approach/prometheus-deployment.yaml
kubectl apply -f ../vanilla_approach/prometheus-config.yaml
kubectl apply -f ../vanilla_approach/grafana-deployment.yaml
kubectl apply -f ../vanilla_approach/otel-collector-deployment.yaml
kubectl apply -f ../vanilla_approach/otel-collector-config.yaml
```

---

## 2. Configure Prometheus to Scrape a Specific Endpoint/Port

Edit your `prometheus-config.yaml` scrape_configs section. Example to scrape Otel Collector on port 4318:

```yaml
scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:4318']
```

Apply the config and restart Prometheus if needed:
```bash
kubectl apply -f ../vanilla_approach/prometheus-config.yaml
kubectl rollout restart deploy/prometheus -n observability
```
for testing Scale the Deployment of ingress-nginx-controller to 0 replicas to use nginx gateway controller instead

Easy to revert (--replicas=1)
```bash
kubectl scale deployment ingress-nginx-controller -n ingress-nginx --replicas=0

kubectl get deploy -n ingress-nginx
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
ingress-nginx-controller   0/0     0            0           29h

```
---

## 3. Deploy Gateway and HTTPRoute

```bash
kubectl apply -f gateway.yaml

kubectl apply -f http-route.yaml

kubectl get gateway -A
NAMESPACE       NAME                    CLASS   ADDRESS           PROGRAMMED   AGE
observability   observability-gateway   nginx   135.116.220.146   True         69s

kubectl get HTTPRoute -A
NAMESPACE       NAME                       HOSTNAMES                                      AGE
observability   observability-http-route   ["demo-gateway.swedencentral.cloudapp.azure.com"]   52s
```

---

## 4. Verify and Test

```bash
kubectl get gatewayclass -A
kubectl get gateway -n observability
kubectl get httproute -n observability
kubectl get svc -n observability
```

- Prometheus: http://demo-gateway.swedencentral.cloudapp.azure.com/prometheus
- Grafana: http://demo-gateway.swedencentral.cloudapp.azure.com/grafana
- Otel Collector: http://demo-gateway.swedencentral.cloudapp.azure.com/v1/metrics

Otel page will show 
`405 method not allowed, supported: [POST]`

---

## 5. Run python script 
Set this in `simple-metrics-sender.py`:
   ```python
   endpoint = os.getenv("OTEL_ENDPOINT", "http://demo-gateway.swedencentral.cloudapp.azure.com/v1/metrics")
   ```  

```bash

python simple-metrics-sender.py 
📊 [00:48:20] Sent metrics: requests=860, duration=0.318s
📊 [00:48:22] Sent metrics: requests=861, duration=0.262s
📊 [00:48:24] Sent metrics: requests=862, duration=0.118s
📊 [00:48:26] Sent metrics: requests=863, duration=0.570s
📊 [00:48:28] Sent metrics: requests=864, duration=0.526s
📊 [00:48:30] Sent metrics: requests=865, duration=0.496s
```
---

## 6. Run the test

1. check otel page will show the following to indicate otel is working properly.
   `http://demo-gateway.swedencentral.cloudapp.azure.com/v1/metrics`  

   `405 method not allowed, supported: [POST]`
 2. check Prometheus and Grafana as above, but use the DNS URLs:
   - Prometheus: http://<DNS>/prometheus http://demo-gateway.swedencentral.cloudapp.azure.com/prometheus
   - Grafana: http://<DNS>/grafana  http://demo-gateway.swedencentral.cloudapp.azure.com/grafana/
      Login: admin / admin
   in grafana-config.yaml set url: `http://demo-gateway.swedencentral.cloudapp.azure.com`
   go to Connections > Data sources > Prometheus > Test connection
   then 
   Explore > Prometheus, and query: `http_requests_total`
5. in grafana-config.yaml set url: `http://demo-gateway.swedencentral.cloudapp.azure.com`
   go to Connections > Data sources > Prometheus > Test connection **Save & Test**
   then 
   Explore > Prometheus, and query: `http_requests_total`

---

## Notes
- Adjust service names/ports in the HTTPRoute or Ingress if your services use different names.
- For advanced path rewriting, see your GatewayClass or Ingress controller docs.
- This approach replaces Ingress with Gateway API resources for modern, extensible traffic management.
- See other approach folders for full deployment YAMLs if needed.
