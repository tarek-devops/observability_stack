# Azure Pipeline Test Project (Linux)

This project demonstrates various Azure Pipeline capabilities using YAML files for a Linux environment.

## Project Structure

- `pipelines/` — Contains all Azure Pipeline YAML files and templates.
  - `simple-build.yml` — Minimal pipeline that echoes a message.
  - `build-test-matrix.yml` — Pipeline with a matrix strategy for multiple Python versions.
  - `deploy-template.yml` — Template for deployment steps.
  - `deploy.yml` — Pipeline using the deployment template.

## How to Use

### 1. Initialize Git and Push to Repository

If you haven't already:

```bash
git init
git add .
git commit -m "Initial commit with Azure pipeline examples"
git branch --unset-upstream
git push origin master
git push origin develop:master
```

### 2. Set Up Azure Pipelines

1. Go to your Azure DevOps project.
2. Navigate to **Pipelines > Create Pipeline**.
3. Select your repository.
4. Choose "Existing Azure Pipelines YAML file" and select one of the YAML files from the `pipelines/` directory.
5. Save and run.

### 3. Triggering Pipelines

- Pipelines are triggered on pushes to the `main` branch by default (`trigger: - main`).
- You can manually run pipelines from the Azure DevOps UI.

## Pipeline Capabilities

### `simple-build.yml`
- Runs a basic script on Ubuntu.

### `build-test-matrix.yml`
- Demonstrates matrix builds for Python 3.8, 3.9, and 3.10.
- Installs dependencies and runs tests (expects a `requirements.txt` and tests in the repo).

### `deploy-template.yml` & `deploy.yml`
- Shows how to use templates for deployment steps.
- `deploy.yml` uses the template to deploy to the `production` environment.

## Customization
- Edit YAML files in `pipelines/` to fit your project needs.
- Add more templates or steps as required.

## Notes
- Make sure your repo contains any files referenced by the pipelines (e.g., `requirements.txt`, test scripts).
- For more advanced scenarios, see [Azure Pipelines documentation](https://docs.microsoft.com/azure/devops/pipelines/yaml-schema).

## How to Set Up a Self-hosted Azure Pipeline Agent (Linux)

Follow these steps to run Azure Pipelines on your own machine:

1. **Go to Azure DevOps > Organization Settings > Agent Pools**
   - Click "Add Pool" if you want a new pool, or use "Default".

2. **Add a New Agent**
   - Click your pool, then "New agent".
   - Select your OS (Linux).
   - Download the agent package (e.g., `vsts-agent-linux-x64-*.tar.gz`).

3. **Prepare the Agent Directory**
   ```bash
   mkdir myagent && cd myagent
   # Download and extract the agent package here
   tar zxvf vsts-agent-linux-x64-4.264.2.tar
   ```

4. **Configure the Agent**
   - Copy the registration command from Azure DevOps, or run:
   ```bash
   ./config.sh
   # Follow prompts: enter your Azure DevOps URL, PAT (Personal Access Token), agent pool, and agent name
   Enter server URL:
     https://dev.azure.com/tarekderi0145
   Enter authentication type (press enter for PAT)
    Click your user icon (top right) and select "Personal access tokens" then Click "New Token"
   
   ```

5. **Run the Agent**
   ```bash
   ./run.sh
   # Or run as a service (recommended for production):
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

6. **Verify**
   - In Azure DevOps, your agent should show as "online" in the agent pool.

7. **Trigger Your Pipeline**
   - Pipelines will now run on your self-hosted agent when triggered.

```bash
   az pipelines list --output table
   az pipelines validate --name env_pipeline--path ./pipelines/env-artifact-pipeline.yml 
```

**References:**
- [Microsoft Docs: Self-hosted Linux agent](https://learn.microsoft.com/azure/devops/pipelines/agents/v2-linux)
- [Personal Access Token setup](https://learn.microsoft.com/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
