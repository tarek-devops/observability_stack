# Live Assignment Tasks

## Task 1: Kubernetes Observability Stack (20 min)

**Goal:** Deploy Prometheus, Grafana, and OpenTelemetry Collector in a provided Kubernetes cluster/namespace. Validate with an external metrics application.

### Steps:
1. Connect to the provided cluster and namespace (credentials will be given).
2. Review provided manifests; identify and create the missing manifest (e.g., OpenTelemetry Collector or config).
3. Apply all manifests:
   ```bash
   kubectl apply -f <manifest>
   ```
4. Port-forward services for access (Grafana, Prometheus, OpenTelemetry Collector).
5. Start the external metrics application (.exe) as instructed.
6. Verify metrics flow into Prometheus and Grafana.
7. Be ready to discuss your approach and troubleshooting steps.

## Task 2: Azure DevOps Pipeline Update (20 min)

**Goal:** Update a provided Azure DevOps pipeline (Linux or Windows) to produce correct output by adding up to 5 steps. Commit and push each change.

### Steps:
1. Clone the provided git repository.
2. Review the pipeline YAML file (`azure-pipelines.yml`).
3. Add up to 5 steps using bash (Linux) or PowerShell (Windows):
   - Print Hello World
   - Show environment variables
   - Check disk space
   - Download a file
   - Archive workspace
4. After each change:
   - `git add azure-pipelines.yml`
   - `git commit -m "Add <step description>"`
   - `git push`
5. Monitor pipeline runs in Azure DevOps UI for correct output.
6. Be ready to discuss your approach and troubleshooting steps.
