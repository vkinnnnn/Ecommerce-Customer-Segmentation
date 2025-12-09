# E-commerce Customer Analytics & Segmentation Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MLOps](https://img.shields.io/badge/MLOps-Enabled-green.svg)](https://ml-ops.org/)

<p align="center">
    <img src="resources/banner.png" alt="Customer Segmentation Platform" width="800"/>
</p>

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Dataset Information](#dataset-information)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Pipeline Components](#pipeline-components)
- [Machine Learning](#machine-learning)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The **E-commerce Customer Analytics & Segmentation Platform** is an end-to-end MLOps solution designed to help businesses understand their customers through advanced data analytics and machine learning. By leveraging unsupervised learning techniques, particularly K-Means clustering, this platform segments customers based on behavioral patterns, purchase history, and demographic characteristics.

### Business Value

- **Personalized Marketing**: Target specific customer segments with tailored campaigns
- **Revenue Optimization**: Identify high-value customers and growth opportunities
- **Churn Prevention**: Detect at-risk customers through behavioral analysis
- **Product Strategy**: Understand product preferences across customer segments
- **Resource Allocation**: Optimize marketing spend based on customer value

## ✨ Key Features

### Data Processing
- **Automated ETL Pipeline**: Streamlined data ingestion and transformation
- **Data Quality Assurance**: Comprehensive validation and cleaning
- **Feature Engineering**: Advanced RFM analysis and behavioral metrics
- **Scalable Architecture**: Handles large-scale transaction datasets

### Machine Learning
- **Customer Segmentation**: K-Means clustering with hyperparameter optimization
- **Dimensionality Reduction**: PCA for visualization and performance
- **Model Versioning**: MLflow integration for experiment tracking
- **Automated Retraining**: Drift detection and model updates

### MLOps Infrastructure
- **Containerization**: Docker-based deployment
- **Orchestration**: Apache Airflow for workflow management
- **Version Control**: DVC for data and model versioning
- **Cloud Integration**: Google Cloud Platform deployment
- **CI/CD**: Automated testing and deployment pipelines
- **Monitoring**: Real-time model performance tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Data Fetcher │→│Archive Extract│→│Dataset Loader │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Processing Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Null Handler │→│  Deduplicator │→│ Code Detector │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Desc Cleaner  │→│Price Validator│→│Transaction Proc│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Feature Engineering Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │RFM Analyzer  │→│Product Aggreg │→│Behavior Analyzer│    │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Location Build│→│Cancel Analyzer│→│Temporal Extract│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Machine Learning Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Outlier Remove│→│Feature Scaler │→│  PCA Transform│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                   ┌──────────────┐                          │
│                   │ K-Means Model│                          │
│                   └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Vertex AI   │  │  Flask API   │  │  Monitoring  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Dataset Information

### Source
UCI Machine Learning Repository - Online Retail Dataset

### Description
Transnational dataset containing all transactions for a UK-based online retail company between **December 2010** and **December 2011**. The company specializes in unique all-occasion gifts, with many wholesale customers.

### Dataset Specifications

| Attribute | Details |
|-----------|---------|
| **Size** | 541,909 transactions × 8 features |
| **Time Period** | 12 months (Dec 2010 - Dec 2011) |
| **Geography** | 38 countries |
| **Customers** | 4,372 unique customers |
| **Products** | 3,684 unique stock codes |

### Features

| Column | Type | Description |
|--------|------|-------------|
| **InvoiceNo** | Categorical | 6-digit unique transaction identifier (prefix 'C' indicates cancellation) |
| **StockCode** | Categorical | 5-digit unique product identifier |
| **Description** | Text | Product name and description |
| **Quantity** | Integer | Number of items per transaction |
| **InvoiceDate** | DateTime | Transaction timestamp |
| **UnitPrice** | Float | Product price per unit (£) |
| **CustomerID** | Categorical | 5-digit unique customer identifier |
| **Country** | Categorical | Customer's country of residence |

## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Docker**: Latest version with daemon running
- **Git**: For version control
- **Memory**: Minimum 8GB RAM recommended

### System Requirements Check

```bash
# Check Python version
python --version  # Should be 3.8+

# Check Docker
docker --version
docker ps  # Verify Docker daemon is running

# Check available memory
docker run --rm "debian:bullseye-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'
```

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/CustomerSegmentationPlatform.git
cd CustomerSegmentationPlatform
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment

**For Windows Users**: Create `.env` file in project root:

```env
AIRFLOW_UID=50000
AIRFLOW__CORE__LOAD_EXAMPLES=false
```

#### 5. Initialize Airflow Database

```bash
# One-time initialization
docker compose up airflow-init
```

#### 6. Start Services

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

Wait for the message:
```
airflow-webserver-1  | 127.0.0.1 - - [DATE] "GET /health HTTP/1.1" 200 141
```

#### 7. Access Airflow UI

Navigate to: `http://localhost:8080`

**Default Credentials:**
- Username: `airflow2`
- Password: `airflow2`

## 🎮 Quick Start

### Running the Complete Pipeline

1. **Access Airflow Dashboard**: `http://localhost:8080`
2. **Locate DAG**: Find `customer_segmentation_workflow`
3. **Trigger DAG**: Click the play button (▶️)
4. **Monitor Progress**: Watch task execution in real-time
5. **View Results**: Check `datasets/processed/` for outputs

### Running Individual Modules

```python
from modules import fetchDataset, loadDataset, analyzeCustomerValue

# Download dataset
archive_path = fetchDataset()

# Load dataset
data_path = loadDataset()

# Perform RFM analysis
rfm_path = analyzeCustomerValue()
```

### Stopping Services

```bash
# Stop all containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

## 📁 Project Structure

```
CustomerSegmentationPlatform/
├── modules/                    # Core processing modules
│   ├── dataFetcher.py         # Data download
│   ├── archiveExtractor.py    # Archive extraction
│   ├── datasetLoader.py       # Data loading
│   ├── nullValueProcessor.py  # Missing value handling
│   ├── recordDeduplicator.py  # Duplicate removal
│   ├── transactionProcessor.py # Transaction classification
│   ├── codeAnomalyDetector.py # Code validation
│   ├── descriptionCleaner.py  # Description cleaning
│   ├── priceValidator.py      # Price validation
│   ├── customerValueAnalyzer.py # RFM analysis
│   ├── productAggregator.py   # Product metrics
│   ├── behaviorAnalyzer.py    # Behavior patterns
│   ├── locationFeatureBuilder.py # Geographic features
│   ├── cancellationAnalyzer.py # Cancellation analysis
│   ├── temporalPatternExtractor.py # Temporal features
│   └── outlierRemover.py      # Outlier detection
├── workflows/                  # Airflow DAG definitions
│   ├── customer_segmentation_dag.py
│   └── model_training_dag.py
├── tests/                      # Test suites
│   ├── test_data_processing.py
│   ├── test_feature_engineering.py
│   └── test_model_pipeline.py
├── datasets/                   # Data storage
│   ├── raw/                   # Original datasets
│   ├── processed/             # Processed datasets
│   └── features/              # Feature matrices
├── cloud_deployment/           # GCP deployment
│   ├── trainer/               # Model training
│   ├── serve/                 # Model serving
│   └── build.py               # Pipeline builder
├── configuration/              # Configuration files
│   ├── model_config.yaml
│   └── pipeline_config.yaml
├── resources/                  # Assets and documentation
│   ├── images/
│   └── diagrams/
├── experiment_tracking/        # MLflow artifacts
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── .dvcignore                 # DVC ignore rules
├── README.md                  # This file
└── LICENSE                    # License information
```

## 🔄 Pipeline Components

### Data Acquisition Pipeline

**Modules**: `dataFetcher` → `archiveExtractor` → `datasetLoader`

Downloads the UCI Online Retail dataset, extracts the archive, and loads data into memory with automatic pickle caching for performance.

### Data Cleaning Pipeline

**Modules**: `nullValueProcessor` → `recordDeduplicator` → `transactionProcessor` → `codeAnomalyDetector` → `descriptionCleaner` → `priceValidator`

Comprehensive data quality assurance including:
- Missing value imputation
- Duplicate record removal
- Transaction status classification
- Anomalous code detection
- Description standardization
- Price validation

### Feature Engineering Pipeline

**Modules**: `customerValueAnalyzer` → `productAggregator` → `behaviorAnalyzer` → `locationFeatureBuilder` → `cancellationAnalyzer` → `temporalPatternExtractor`

Creates rich customer features:
- **RFM Metrics**: Recency, Frequency, Monetary value
- **Product Diversity**: Unique products purchased
- **Behavioral Patterns**: Shopping day/hour preferences
- **Geographic Indicators**: Location-based features
- **Cancellation Metrics**: Return behavior analysis
- **Temporal Trends**: Seasonality and spending trajectories

### Model Training Pipeline

**Modules**: `outlierRemover` → `featureNormalizer` → `dimensionalityReducer` → `clusteringModel`

Machine learning workflow:
- Isolation Forest outlier detection
- StandardScaler normalization
- PCA dimensionality reduction
- K-Means clustering with hyperparameter tuning

## 🤖 Machine Learning

### Clustering Algorithm

**K-Means Clustering** with the following optimizations:
- Hyperparameter tuning (n_clusters, init method, n_init, max_iter)
- Silhouette score optimization
- Davies-Bouldin Index minimization
- Calinski-Harabasz Index maximization

### Model Evaluation Metrics

| Metric | Description | Optimal Value |
|--------|-------------|---------------|
| **Silhouette Score** | Cluster cohesion and separation | Closer to +1 |
| **Davies-Bouldin Index** | Average similarity ratio | Lower is better |
| **Calinski-Harabasz Index** | Ratio of between/within cluster dispersion | Higher is better |

### Experiment Tracking

MLflow integration provides:
- Parameter logging
- Metric tracking
- Model versioning
- Artifact storage
- Experiment comparison

Access MLflow UI: `http://localhost:5000`

## 🚢 Deployment

### Google Cloud Platform

The platform deploys to GCP using:
- **Vertex AI**: Model training and serving
- **Cloud Storage**: Data and model storage
- **BigQuery**: Monitoring data warehouse
- **Looker Studio**: Visualization dashboards

### Deployment Steps

```bash
# Build Docker images
cd cloud_deployment
docker build -t trainer:latest ./trainer
docker build -t serve:latest ./serve

# Push to Artifact Registry
docker tag trainer:latest gcr.io/PROJECT_ID/trainer:latest
docker push gcr.io/PROJECT_ID/trainer:latest

# Deploy to Vertex AI
python build.py --project PROJECT_ID --region us-east1
```

### API Endpoint

```python
import requests

# Prediction request
response = requests.post(
    'https://ENDPOINT_URL/predict',
    json={
        'instances': [{
            'Days_Since_Last_Purchase': 30,
            'Total_Transactions': 15,
            'Total_Spend': 500.0,
            # ... other features
        }]
    }
)

cluster = response.json()['predictions'][0]
```

## 📈 Monitoring

### Performance Metrics

- **Latency**: Request/response time
- **Throughput**: Requests per second
- **Error Rate**: Failed predictions
- **Data Drift**: Feature distribution changes
- **Concept Drift**: Model performance degradation

### Monitoring Dashboard

Access real-time monitoring: [Looker Studio Dashboard](https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID)

Tracks:
- Model prediction latency
- Feature min/max values
- Cluster distribution
- API usage statistics

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_data_processing.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Linting
ruff check modules/

# Type checking
mypy modules/

# Format code
ruff format modules/
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- UCI Machine Learning Repository for the dataset
- Apache Airflow community
- MLflow development team
- Google Cloud Platform
- Open source contributors

## 📞 Support

For questions, issues, or feature requests:
- **Issues**: [GitHub Issues](https://github.com/yourusername/CustomerSegmentationPlatform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/CustomerSegmentationPlatform/discussions)
- **Email**: support@yourcompany.com

---

**Built with ❤️ for data-driven customer insights**
