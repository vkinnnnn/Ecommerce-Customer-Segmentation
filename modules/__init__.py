"""
Customer Segmentation Platform - Data Processing Modules

This package contains all data processing, feature engineering, and analysis
modules for the e-commerce customer segmentation platform.

Module Categories
-----------------
Data Acquisition:
    - dataFetcher: Download datasets from remote sources
    - archiveExtractor: Extract compressed dataset archives
    - datasetLoader: Load datasets from various formats

Data Cleaning:
    - nullValueProcessor: Handle missing values
    - recordDeduplicator: Remove duplicate records
    - transactionProcessor: Classify transaction status
    - codeAnomalyDetector: Detect and remove anomalous codes
    - descriptionCleaner: Clean and standardize descriptions
    - priceValidator: Validate pricing data

Feature Engineering:
    - customerValueAnalyzer: RFM analysis
    - productAggregator: Product diversity metrics
    - behaviorAnalyzer: Shopping behavior patterns
    - locationFeatureBuilder: Geographic features
    - cancellationAnalyzer: Cancellation patterns
    - temporalPatternExtractor: Seasonal trends

Advanced Analytics:
    - outlierRemover: Outlier detection and removal
    - dimensionalityReducer: PCA transformation
    - featureNormalizer: Feature scaling

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Customer Analytics Team"

# Data Acquisition Modules
from .dataFetcher import fetchDataset
from .archiveExtractor import extractArchive
from .datasetLoader import loadDataset

# Data Cleaning Modules
from .nullValueProcessor import processMissingValues
from .recordDeduplicator import eliminateDuplicates
from .transactionProcessor import classifyTransactionStatus
from .codeAnomalyDetector import detectCodeAnomalies
from .descriptionCleaner import cleanDescriptions
from .priceValidator import validatePricing

# Feature Engineering Modules
from .customerValueAnalyzer import analyzeCustomerValue
from .productAggregator import aggregateProductData
from .behaviorAnalyzer import analyzeBehaviorPatterns
from .locationFeatureBuilder import buildLocationFeatures
from .cancellationAnalyzer import analyzeCancellations
from .temporalPatternExtractor import extractTemporalPatterns

# Advanced Analytics Modules
from .outlierRemover import removeOutliers

__all__ = [
    # Data Acquisition
    'fetchDataset',
    'extractArchive',
    'loadDataset',
    # Data Cleaning
    'processMissingValues',
    'eliminateDuplicates',
    'classifyTransactionStatus',
    'detectCodeAnomalies',
    'cleanDescriptions',
    'validatePricing',
    # Feature Engineering
    'analyzeCustomerValue',
    'aggregateProductData',
    'analyzeBehaviorPatterns',
    'buildLocationFeatures',
    'analyzeCancellations',
    'extractTemporalPatterns',
    # Advanced Analytics
    'removeOutliers',
]
