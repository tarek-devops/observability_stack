Key Ports

4317: OTLP gRPC
4318: OTLP HTTP
9090: Prometheus
3000: Grafana

# Service Type: ClusterIP for Promethous, otel, Grafana without any ingress controller
```bash
kubectl get pods -n observability -o wide
NAME                              READY   STATUS    RESTARTS   AGE     IP             NODE  OMINATED NODE   READINESS GATES
otel-collector-5756646988-5nvsr   1/1     Running   0   2m36s   10.244.1.112   aks-nodepool1-14987286-vmss000001   <none>           <none>
prometheus-778588f7bf-ltrvt       1/1     Running   0          22s   10.244.1.140   aks-nodepool1-14987286-vmss000001   <none>           <none>
grafana-599cc6f5b7-27ml7          1/1     Running   0          25s   10.244.1.216   aks-nodepool1-14987286-vmss000001   <none>           <none>
```

```bash
kubectl get svc -n observability -o wide
NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE    SELECTOR
otel-collector   ClusterIP   10.0.198.103   <none>        4317/TCP,4318/TCP,8889/TCP   3m6s   app=otel-collector
prometheus       ClusterIP   10.0.212.61    <none>        9090/TCP                     52s   app=prometheus
grafana          NodePort    10.0.236.29    <none>        3000:32000/TCP               7s    app=grafana
```

# Service Type: LoadBalancer , otel, Grafana , ClusterIP for Prometheus
Both grafana service and otel-collector service have own public IP address
 135.225.7.29:3000
 9.223.17.201:4318
 We used port-forwarding for prometheus
```bash
kubectl get services -n observability
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)                                        AGE
grafana          LoadBalancer   10.0.236.29    135.225.7.29   3000:32000/TCP                                 5h4m
otel-collector   LoadBalancer   10.0.198.103   9.223.17.201   4317:32579/TCP,4318:31761/TCP,8889:32334/TCP   5h26m
prometheus       ClusterIP      10.0.212.61    <none>         9090/TCP                                       5h14m
```
# Service Type: ClusterIP for otel, Grafana , Prometheus with ingress manifest
All Prometheus service and grafana service and otel-collector service have the same public IP address, the IP is belong the ingress controller IP
20.240.74.223/grafana
20.240.74.223/prometheus
20.240.74.223/collector/v1/metrics
but ingress manifest requires to have DNS instead of IP, Azure Portal: Go to Public IP addresses → select your IP → Settings > Configuration, set DNS name label as observability-demo
so DNS name is observability-demo.swedencentral.cloudapp.azure.com
http://observability-demo.swedencentral.cloudapp.azure.com/prometheus
```bash
kubectl get svc -n observability
NAME             TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
grafana          ClusterIP   10.0.236.29    <none>        3000/TCP                     2d3h
otel-collector   ClusterIP   10.0.198.103   <none>        4317/TCP,4318/TCP,8889/TCP   2d3h
prometheus       ClusterIP   10.0.212.61    <none>        9090/TCP                     2d3h

kubectl get svc -n ingress-basic
NAME                                 TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)                      AGE
ingress-nginx-controller             LoadBalancer   10.0.190.1    20.240.74.223   80:30657/TCP,443:30690/TCP   22m
ingress-nginx-controller-admission   ClusterIP      10.0.207.13   <none>          443/TCP                      22m

kubectl get ingress/observability-ingress -n observability
NAME                    CLASS    HOSTS                                                 ADDRESS   PORTS   AGE
observability-ingress   <none>   observability-demo.swedencentral.cloudapp.azure.com             80      10m
```

## Critical Points:

- Service type: LoadBalancer (or NodePort if LoadBalancer unavailable)
- Ports: 4317 (gRPC), 4318 (HTTP)
- Selector must match deployment labels

Common Pitfalls to Avoid
Kubernetes:

❌ Forgetting namespace -n observability
❌ Wrong port numbers (4317 vs 4318)
❌ Service selector not matching deployment labels
❌ Using type: ClusterIP instead of LoadBalancer


```bash
# Pod not starting
kubectl describe pod <pod-name> -n observability

kubectl logs <pod-name> -n observability

# Service no external IP (use NodePort instead)
kubectl patch svc otel-collector -n observability -p '{"spec":{"type":"NodePort"}}'

# Test connectivity
kubectl port-forward -n observability svc/otel-collector 4318:4318
curl http://localhost:4318/v1/metrics

# Full reset
kubectl delete namespace observability
kubectl apply -f kubernetes/
```

### If Kubernetes LoadBalancer doesn't work:
```bash
# Use NodePort
kubectl patch svc otel-collector -n observability -p '{"spec":{"type":"NodePort"}}'

# Or port-forward
kubectl port-forward -n observability svc/otel-collector 4317:4317 4318:4318
```

## Azure Pipelines
```bash
# Pipeline not triggering
# Check trigger branch matches your branch
git branch

# Variable not expanding
# Use double quotes: "$(var)" not '$(var)'

# Path not found
# Always check with: Test-Path (PowerShell) or ls (Bash)

# Git commit fails
git config user.email "you@example.com"
git config user.name "Your Name"
```

Azure Pipelines:

❌ Not committing after each step
❌ Wrong variable syntax: '$(var)' vs "$(var)"
❌ Path issues: Always use relative paths
❌ Forgetting to add files to artifacts before publishing