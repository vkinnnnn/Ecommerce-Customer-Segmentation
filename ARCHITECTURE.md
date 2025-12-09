# System Architecture Documentation

## Customer Segmentation Platform - Technical Architecture

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Data Flow](#data-flow)
- [Module Architecture](#module-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability](#scalability)

---

## Overview

The Customer Segmentation Platform is built on a **modular, pipeline-based architecture** that enables:
- **Scalability**: Process large datasets efficiently
- **Maintainability**: Independent, testable modules
- **Extensibility**: Easy to add new features
- **Reliability**: Robust error handling and logging

### Architecture Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Loose Coupling**: Modules communicate through file I/O
3. **High Cohesion**: Related functionality grouped together
4. **Fail-Fast**: Early validation and error detection
5. **Observability**: Comprehensive logging and monitoring

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                  (Airflow Web UI / API)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│                      (Apache Airflow)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Pipeline│  │ Model Training│  │  Monitoring  │          │
│  │     DAG      │  │     DAG      │  │     DAG      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Data Acquisition Modules                     │  │
│  │  dataFetcher → archiveExtractor → datasetLoader          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Data Cleaning Modules                        │  │
│  │  nullValueProcessor → recordDeduplicator →               │  │
│  │  transactionProcessor → codeAnomalyDetector →            │  │
│  │  descriptionCleaner → priceValidator                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Feature Engineering Modules                    │  │
│  │  customerValueAnalyzer → productAggregator →             │  │
│  │  behaviorAnalyzer → locationFeatureBuilder →             │  │
│  │  cancellationAnalyzer → temporalPatternExtractor         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Machine Learning Modules                       │  │
│  │  outlierRemover → featureNormalizer →                    │  │
│  │  dimensionalityReducer → clusteringModel                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  File System │  │  Google Cloud│  │    DVC       │          │
│  │   (Pickle)   │  │   Storage    │  │  (Versioning)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Vertex AI   │  │  Flask API   │  │   BigQuery   │          │
│  │  (Training)  │  │  (Serving)   │  │ (Monitoring) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    MLflow    │  │Looker Studio │  │ Prometheus   │          │
│  │ (Experiments)│  │ (Dashboards) │  │   (Metrics)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Pipeline Data Flow

```
┌─────────────┐
│   UCI Repo  │ (Remote Dataset Source)
└──────┬──────┘
       │ HTTP Download
       ↓
┌─────────────┐
│ retail_data │ (ZIP Archive)
│    .zip     │
└──────┬──────┘
       │ Extract
       ↓
┌─────────────┐
│Online Retail│ (Excel File)
│    .xlsx    │
└──────┬──────┘
       │ Load
       ↓
┌─────────────┐
│transaction_ │ (Pickle - Raw Data)
│  data.pkl   │
└──────┬──────┘
       │ Clean Nulls
       ↓
┌─────────────┐
│ cleaned_    │ (Pickle - No Nulls)
│  nulls.pkl  │
└──────┬──────┘
       │ Deduplicate
       ↓
┌─────────────┐
│deduplicated_│ (Pickle - Unique Records)
│  data.pkl   │
└──────┬──────┘
       │ Classify Transactions
       ↓
┌─────────────┐
│transaction_ │ (Pickle - Status Added)
│classified.pkl│
└──────┬──────┘
       │ Detect Anomalies
       ↓
┌─────────────┐
│   code_     │ (Pickle - Valid Codes)
│validated.pkl│
└──────┬──────┘
       │ Clean Descriptions
       ↓
┌─────────────┐
│description_ │ (Pickle - Clean Text)
│ cleaned.pkl │
└──────┬──────┘
       │ Validate Prices
       ↓
┌─────────────┐
│   price_    │ (Pickle - Valid Prices)
│validated.pkl│
└──────┬──────┘
       │ RFM Analysis
       ↓
┌─────────────┐
│    rfm_     │ (Pickle - Customer Metrics)
│ analysis.pkl│
└──────┬──────┘
       │ Aggregate Products
       ↓
┌─────────────┐
│  product_   │ (Pickle - Product Metrics)
│aggregated.pkl│
└──────┬──────┘
       │ Analyze Behavior
       ↓
┌─────────────┐
│  behavior_  │ (Pickle - Behavior Metrics)
│ analyzed.pkl│
└──────┬──────┘
       │ Build Location Features
       ↓
┌─────────────┐
│  location_  │ (Pickle - Geographic Features)
│ features.pkl│
└──────┬──────┘
       │ Analyze Cancellations
       ↓
┌─────────────┐
│cancellation_│ (Pickle - Cancellation Metrics)
│ analyzed.pkl│
└──────┬──────┘
       │ Extract Temporal Patterns
       ↓
┌─────────────┐
│  temporal_  │ (Pickle - Temporal Features)
│ features.pkl│
└──────┬──────┘
       │ Remove Outliers
       ↓
┌─────────────┐
│  outliers_  │ (Pickle - Clean Features)
│  removed.pkl│
└──────┬──────┘
       │ Scale Features
       ↓
┌─────────────┐
│   scaled_   │ (Pickle - Normalized Features)
│ features.pkl│
└──────┬──────┘
       │ PCA Transform
       ↓
┌─────────────┐
│     pca_    │ (Pickle - Reduced Dimensions)
│transformed.pkl│
└──────┬──────┘
       │ K-Means Clustering
       ↓
┌─────────────┐
│  customer_  │ (Pickle - Final Segments)
│ segments.pkl│
└─────────────┘
```

---

## Module Architecture

### Module Design Pattern

Each module follows a consistent design pattern:

```python
"""
Module Documentation
"""

import dependencies
from pathlib import Path

# Configuration Constants
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PATH = PROJECT_ROOT / 'datasets' / 'input.pkl'
OUTPUT_PATH = PROJECT_ROOT / 'datasets' / 'output.pkl'

def moduleFunction(sourcePath=SOURCE_PATH, outputPath=OUTPUT_PATH):
    """
    Function documentation with NumPy style.
    
    Parameters
    ----------
    sourcePath : str or Path
        Input file path
    outputPath : str or Path
        Output file path
        
    Returns
    -------
    str
        Path to output file
        
    Raises
    ------
    FileNotFoundError
        If source file doesn't exist
    """
    # Convert to Path objects
    sourcePath = Path(sourcePath)
    outputPath = Path(outputPath)
    
    # Print header
    print("=" * 60)
    print("MODULE NAME")
    print("=" * 60)
    
    # Validate input
    if not sourcePath.exists():
        raise FileNotFoundError(f"Source not found: {sourcePath}")
    
    # Load data
    with open(sourcePath, "rb") as f:
        data = pickle.load(f)
    
    # Process data
    processed_data = process(data)
    
    # Validate output
    validate(processed_data)
    
    # Save data
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    with open(outputPath, "wb") as f:
        pickle.dump(processed_data, f)
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("✓ PROCESSING COMPLETED")
    print(f"{'=' * 60}")
    
    return str(outputPath)
```

### Module Categories

#### 1. Data Acquisition Modules
**Purpose**: Download and prepare raw data  
**Input**: External URLs or archives  
**Output**: Pickle files with raw data  
**Error Handling**: Network errors, file I/O errors

#### 2. Data Cleaning Modules
**Purpose**: Ensure data quality  
**Input**: Raw or partially cleaned pickle files  
**Output**: Cleaned pickle files  
**Error Handling**: Validation errors, data quality issues

#### 3. Feature Engineering Modules
**Purpose**: Create analytical features  
**Input**: Cleaned transaction data  
**Output**: Customer-level feature matrices  
**Error Handling**: Calculation errors, missing data

#### 4. Advanced Analytics Modules
**Purpose**: Prepare data for modeling  
**Input**: Feature matrices  
**Output**: Model-ready datasets  
**Error Handling**: Algorithm errors, convergence issues

---

## Deployment Architecture

### Docker Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                           │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Airflow Webserver Container            │    │
│  │  - Flask Web UI                                │    │
│  │  - Port 8080                                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Airflow Scheduler Container            │    │
│  │  - DAG Scheduling                              │    │
│  │  - Task Execution                              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Airflow Worker Container(s)            │    │
│  │  - Task Processing                             │    │
│  │  - Module Execution                            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         PostgreSQL Container                   │    │
│  │  - Airflow Metadata                            │    │
│  │  - Port 5432                                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Redis Container                        │    │
│  │  - Celery Broker                               │    │
│  │  - Port 6379                                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         MLflow Container                       │    │
│  │  - Experiment Tracking                         │    │
│  │  - Port 5000                                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Shared Volumes                         │    │
│  │  - /datasets (Data storage)                    │    │
│  │  - /modules (Code)                             │    │
│  │  - /logs (Logs)                                │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Google Cloud Platform Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Google Cloud Platform                  │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Cloud Storage Buckets                  │    │
│  │  - Raw Data Storage                            │    │
│  │  - Processed Data Storage                      │    │
│  │  - Model Artifacts                             │    │
│  │  - DVC Remote                                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Vertex AI                              │    │
│  │  ┌──────────────────────────────────────────┐ │    │
│  │  │  Training Jobs                           │ │    │
│  │  │  - Custom Container Training             │ │    │
│  │  │  - Hyperparameter Tuning                 │ │    │
│  │  └──────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────┐ │    │
│  │  │  Model Registry                          │ │    │
│  │  │  - Model Versioning                      │ │    │
│  │  │  - Model Metadata                        │ │    │
│  │  └──────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────┐ │    │
│  │  │  Endpoints                               │ │    │
│  │  │  - Model Serving                         │ │    │
│  │  │  - Auto-scaling                          │ │    │
│  │  └──────────────────────────────────────────┘ │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         BigQuery                               │    │
│  │  - Prediction Logs                             │    │
│  │  - Monitoring Data                             │    │
│  │  - Analytics Queries                           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Looker Studio                          │    │
│  │  - Real-time Dashboards                        │    │
│  │  - Performance Metrics                         │    │
│  │  - Drift Detection                             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Artifact Registry                      │    │
│  │  - Docker Images                               │    │
│  │  - Training Containers                         │    │
│  │  - Serving Containers                          │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.8+ | Core development language |
| **Data Processing** | Pandas, NumPy | Data manipulation |
| **ML Framework** | Scikit-learn | Clustering algorithms |
| **Deep Learning** | TensorFlow | Advanced modeling |
| **Orchestration** | Apache Airflow | Workflow management |
| **Containerization** | Docker | Application packaging |
| **Version Control** | Git, DVC | Code and data versioning |
| **Experiment Tracking** | MLflow | ML experiment management |
| **Cloud Platform** | Google Cloud | Deployment infrastructure |
| **API Framework** | Flask | Model serving |
| **Testing** | Pytest | Unit and integration testing |
| **Code Quality** | Ruff, MyPy | Linting and type checking |

### Dependencies

```
Core: pandas, numpy, scipy
ML: scikit-learn, tensorflow
Orchestration: apache-airflow
Cloud: google-cloud-storage, google-cloud-aiplatform
API: Flask, requests
Testing: pytest, pytest-cov
Quality: ruff, mypy
```

---

## Design Patterns

### 1. Pipeline Pattern
**Description**: Sequential data transformation steps  
**Implementation**: Each module outputs to next module's input  
**Benefits**: Clear data flow, easy debugging, modular testing

### 2. Factory Pattern
**Description**: Standardized module creation  
**Implementation**: All modules follow same interface  
**Benefits**: Consistency, predictability, maintainability

### 3. Strategy Pattern
**Description**: Interchangeable algorithms  
**Implementation**: Different clustering algorithms can be swapped  
**Benefits**: Flexibility, extensibility

### 4. Observer Pattern
**Description**: Event-driven monitoring  
**Implementation**: MLflow tracks experiment changes  
**Benefits**: Real-time tracking, audit trail

### 5. Singleton Pattern
**Description**: Single instance resources  
**Implementation**: Database connections, configuration  
**Benefits**: Resource efficiency, consistency

---

## Scalability

### Horizontal Scaling

```
┌─────────────────────────────────────────┐
│         Load Balancer                    │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ↓         ↓         ↓
    ┌───────┐ ┌───────┐ ┌───────┐
    │Worker1│ │Worker2│ │Worker3│
    └───────┘ └───────┘ └───────┘
```

**Capabilities**:
- Multiple Airflow workers
- Parallel task execution
- Distributed processing

### Vertical Scaling

**Capabilities**:
- Increased worker memory
- More CPU cores
- Larger disk storage

### Data Partitioning

```
Customer Data
    ├── Partition 1 (Customers 1-1000)
    ├── Partition 2 (Customers 1001-2000)
    ├── Partition 3 (Customers 2001-3000)
    └── Partition N (Customers N-1000 to N)
```

**Benefits**:
- Parallel processing
- Reduced memory footprint
- Faster execution

---

## Security Architecture

### Data Security

```
┌─────────────────────────────────────────┐
│         Data at Rest                     │
│  - Encrypted pickle files                │
│  - GCS encryption                        │
│  - Access control lists                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Data in Transit                  │
│  - HTTPS for API calls                   │
│  - TLS for database connections          │
│  - Encrypted file transfers              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Access Control                   │
│  - IAM roles and permissions             │
│  - Service account authentication        │
│  - API key management                    │
└─────────────────────────────────────────┘
```

---

## Monitoring & Observability

### Monitoring Stack

```
Application Logs
    ↓
┌─────────────────┐
│  Python Logging │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Airflow Logs   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  MLflow Metrics │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   BigQuery      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Looker Studio   │
│   Dashboards    │
└─────────────────┘
```

### Key Metrics

- **Pipeline Metrics**: Execution time, success rate, data volume
- **Model Metrics**: Silhouette score, cluster distribution
- **System Metrics**: CPU usage, memory usage, disk I/O
- **Business Metrics**: Customer segments, revenue per segment

---

**Last Updated**: December 2024  
**Version**: 1.0.0
