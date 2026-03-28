# Diamond Price Prediction

An end-to-end machine learning project that predicts diamond price from physical and quality attributes.  
The project includes:

- Data ingestion and train/test split
- Data preprocessing pipeline (numerical + categorical features)
- Model training and model selection based on $R^2$
- Flask web interface for interactive predictions

## Project Overview

The prediction model uses the following input features:

- Numerical: `carat`, `depth`, `table`, `x`, `y`, `z`
- Categorical: `cut`, `color`, `clarity`

Target:

- `price`

The training pipeline reads dataset from:

- `Notebooks/data/gemstone.csv`

It then writes processed outputs and model artifacts to the `artifacts/` folder.

## Tech Stack

- Python
- pandas, numpy
- scikit-learn
- Flask
- seaborn (for analysis notebooks)

## Project Structure

```text
dimondpriceprediction/
|-- application.py                  # Flask app entry point
|-- requirements.txt
|-- setup.py
|-- artifacts/                      # Generated data/model artifacts
|-- Notebooks/
|   |-- EDA.ipynb
|   |-- Model Training.ipynb
|   |-- data/
|       |-- gemstone.csv            # Source dataset used in pipeline
|-- src/
|   |-- exception.py
|   |-- logger.py
|   |-- utils.py
|   |-- components/
|   |   |-- data_ingestion.py
|   |   |-- data_transformation.py
|   |   |-- model_trainer.py
|   |-- pipelines/
|       |-- training_pipeline.py    # Train model and save artifacts
|       |-- prediction_pipeline.py  # Load artifacts and predict
|-- templates/
|   |-- index.html
|   |-- form.html
```

## Workflow

1. Data ingestion
2. Data transformation (imputation, encoding, scaling)
3. Model training and selection
4. Save:
	- `artifacts/preprocessor.pkl`
	- `artifacts/model.pkl`
5. Serve predictions through Flask app

## Setup Instructions

### 1) Clone and open the project

```bash
git clone <your-repository-url>
cd dimondpriceprediction
```

### 2) Create and activate virtual environment (recommended)

Windows (cmd):

```bash
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

## Run Training Pipeline

Generate train/test split, preprocessing object, and trained model:

```bash
python src/pipelines/training_pipeline.py
```

Expected generated artifacts:

- `artifacts/train.csv`
- `artifacts/test.csv`
- `artifacts/data.csv`
- `artifacts/preprocessor.pkl`
- `artifacts/model.pkl`

## Run Flask Application

Start the web app:

```bash
python application.py
```

Open in browser:

- `http://127.0.0.1:5000/`

Available routes:

- `GET /` : Home page
- `GET /predict` : Prediction input form
- `POST /predict` : Submit features and get predicted price

## Input Fields in Web Form

- `carat`
- `depth`
- `table`
- `x`
- `y`
- `z`
- `cut`
- `color`
- `clarity`

## AWS Deployment Guide (Docker + Kubernetes + Prometheus + Grafana)

This section explains how to deploy the Flask app on AWS using:

- Docker
- Amazon ECR (container registry)
- Amazon EKS (Kubernetes cluster)
- Prometheus (monitoring)
- Grafana (dashboards)

### 1) Prerequisites

Install and configure:

- AWS CLI (`aws configure`)
- Docker Desktop / Docker Engine
- `kubectl`
- `eksctl`
- `helm`

Recommended IAM permissions:

- ECR full access (or scoped push/pull access)
- EKS cluster create/manage access
- EC2/VPC permissions required by `eksctl`

### 2) Create Dockerfile

Create a `Dockerfile` in project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "application.py"]
```

Build and test locally:

```bash
docker build -t diamond-price-app:latest .
docker run -p 5000:5000 diamond-price-app:latest
```

### 3) Create ECR Repository and Push Image

Set variables:

```bash
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=<your-account-id>
ECR_REPO=diamond-price-app
IMAGE_TAG=v1
```

Create repository:

```bash
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION
```

Login and push image:

```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag diamond-price-app:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG
```

### 4) Create EKS Cluster

```bash
eksctl create cluster \
  --name diamond-eks \
  --region $AWS_REGION \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --managed
```

Verify:

```bash
kubectl get nodes
```

### 5) Deploy Application to Kubernetes

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: diamond-price-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: diamond-price-app
  template:
    metadata:
      labels:
        app: diamond-price-app
    spec:
      containers:
      - name: diamond-price-app
        image: <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/diamond-price-app:v1
        ports:
        - containerPort: 5000
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: diamond-price-app-service
spec:
  type: LoadBalancer
  selector:
    app: diamond-price-app
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
```

Apply manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
kubectl get svc
```

Use the external LoadBalancer URL from `kubectl get svc` to access the app.

### 6) Install Prometheus and Grafana with Helm

Add Helm repo and install stack:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

Check resources:

```bash
kubectl get pods -n monitoring
```

### 7) Access Grafana Dashboard

Port-forward Grafana service:

```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

Open:

- `http://localhost:3000`

Get Grafana admin password:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 --decode ; echo
```

Default username:

- `admin`

### 8) Expose Application Metrics for Prometheus (Recommended)

For app-level metrics (request count, latency, etc.), add `prometheus-flask-exporter`:

```bash
pip install prometheus-flask-exporter
```

Then initialize metrics in `application.py`:

```python
from prometheus_flask_exporter import PrometheusMetrics

application = Flask(__name__)
metrics = PrometheusMetrics(application)
```

This exposes `/metrics`, which Prometheus can scrape.

### 9) Useful Operations

Restart deployment after image update:

```bash
kubectl rollout restart deployment/diamond-price-app
```

View logs:

```bash
kubectl logs -l app=diamond-price-app --tail=100
```

Scale app:

```bash
kubectl scale deployment diamond-price-app --replicas=4
```

### 10) Cleanup (Avoid AWS Charges)

```bash
eksctl delete cluster --name diamond-eks --region $AWS_REGION
aws ecr delete-repository --repository-name $ECR_REPO --force --region $AWS_REGION
```

## Notes

- Run the training pipeline before using the prediction page, otherwise model files may be missing.
- Logs are saved inside the `logs/` directory with timestamped filenames.
- This repository folder is named `dimondpriceprediction` (spelling retained from the project).

## Author

- Shubham Kumar