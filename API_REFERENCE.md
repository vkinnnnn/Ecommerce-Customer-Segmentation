# API Reference Documentation

## Customer Segmentation Platform - Module API

This document provides detailed API reference for all modules in the Customer Segmentation Platform.

---

## Table of Contents

- [Data Acquisition](#data-acquisition)
- [Data Cleaning](#data-cleaning)
- [Feature Engineering](#feature-engineering)
- [Advanced Analytics](#advanced-analytics)
- [Usage Examples](#usage-examples)

---

## Data Acquisition

### dataFetcher

#### `fetchDataset(sourceUrl, timeoutSeconds)`

Downloads e-commerce dataset from remote URL.

**Parameters:**
- `sourceUrl` (str, optional): Remote URL of dataset archive
  - Default: UCI_DATASET_URL
- `timeoutSeconds` (int, optional): Maximum wait time for server response
  - Default: 45

**Returns:**
- `str`: Absolute path to downloaded archive file

**Raises:**
- `RequestException`: If HTTP request fails
- `Timeout`: If request exceeds timeout
- `IOError`: If file writing fails

**Example:**
```python
from modules import fetchDataset

# Download with default URL
archive_path = fetchDataset()

# Download with custom URL
archive_path = fetchDataset(
    sourceUrl="https://example.com/data.zip",
    timeoutSeconds=60
)
```

---

### archiveExtractor

#### `extractArchive(archiveFilePath, destinationDirectory)`

Extracts compressed dataset archive to specified directory.

**Parameters:**
- `archiveFilePath` (str|Path, optional): Path to ZIP archive
  - Default: ARCHIVE_FILE_PATH
- `destinationDirectory` (str|Path, optional): Extraction destination
  - Default: EXTRACTION_DIRECTORY

**Returns:**
- `str`: Path to primary extracted Excel file

**Raises:**
- `FileNotFoundError`: If archive doesn't exist
- `zipfile.BadZipFile`: If archive is corrupted

**Example:**
```python
from modules import extractArchive

# Extract with defaults
excel_path = extractArchive()

# Extract to custom location
excel_path = extractArchive(
    archiveFilePath="data/custom.zip",
    destinationDirectory="data/extracted"
)
```

---

### datasetLoader

#### `loadDataset(pickleFilePath, excelFilePath)`

Loads e-commerce transaction dataset from available sources.

**Parameters:**
- `pickleFilePath` (str|Path, optional): Path to serialized pickle
  - Default: PICKLE_STORAGE_PATH
- `excelFilePath` (str|Path, optional): Path to source Excel file
  - Default: EXCEL_SOURCE_PATH

**Returns:**
- `str`: Path to persisted pickle file

**Raises:**
- `FileNotFoundError`: If neither pickle nor Excel exists

**Example:**
```python
from modules import loadDataset

# Load with defaults (tries pickle first, then Excel)
data_path = loadDataset()

# Load from specific Excel file
data_path = loadDataset(
    excelFilePath="data/custom_data.xlsx"
)
```

---

## Data Cleaning

### nullValueProcessor

#### `processMissingValues(sourcePicklePath, outputPicklePath)`

Removes records with missing values in critical columns.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
  - Default: SOURCE_PICKLE_PATH
- `outputPicklePath` (str|Path, optional): Output pickle path
  - Default: OUTPUT_PICKLE_PATH

**Returns:**
- `str`: Path to cleaned dataset pickle file

**Raises:**
- `FileNotFoundError`: If source pickle doesn't exist
- `ValueError`: If missing values remain after processing

**Critical Columns:**
- CustomerID
- Description

**Example:**
```python
from modules import processMissingValues

# Process with defaults
cleaned_path = processMissingValues()

# Process custom files
cleaned_path = processMissingValues(
    sourcePicklePath="data/raw.pkl",
    outputPicklePath="data/cleaned.pkl"
)
```

---

### recordDeduplicator

#### `eliminateDuplicates(sourcePicklePath, outputPicklePath)`

Removes duplicate transaction records from dataset.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to deduplicated dataset

**Deduplication Columns:**
- InvoiceNo
- StockCode
- Description
- CustomerID
- Quantity

**Example:**
```python
from modules import eliminateDuplicates

deduped_path = eliminateDuplicates()
```

---

### transactionProcessor

#### `classifyTransactionStatus(sourcePicklePath, outputPicklePath)`

Adds transaction status classification to dataset.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to classified dataset

**Classification Logic:**
- InvoiceNo starts with 'C' → 'Cancelled'
- Otherwise → 'Completed'

**Example:**
```python
from modules import classifyTransactionStatus

classified_path = classifyTransactionStatus()
```

---

### codeAnomalyDetector

#### `detectCodeAnomalies(sourcePicklePath, outputPicklePath)`

Detects and removes records with anomalous stock codes.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to validated dataset

**Detection Criteria:**
- Stock codes with 0 or 1 numeric characters are considered anomalous
- Normal codes have 5-6 digits

**Example:**
```python
from modules import detectCodeAnomalies

validated_path = detectCodeAnomalies()
```

---

### descriptionCleaner

#### `cleanDescriptions(sourcePicklePath, outputPicklePath)`

Cleans and standardizes product descriptions.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to cleaned dataset

**Cleaning Operations:**
- Removes service-related descriptions
- Standardizes to uppercase

**Excluded Descriptions:**
- Next Day Carriage
- High Resolution Image
- POSTAGE
- Manual
- Discount
- Adjust bad debt

**Example:**
```python
from modules import cleanDescriptions

cleaned_path = cleanDescriptions()
```

---

### priceValidator

#### `validatePricing(sourcePicklePath, outputPicklePath)`

Validates and filters records based on unit price.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to validated dataset

**Validation Rule:**
- Removes records where UnitPrice ≤ 0

**Example:**
```python
from modules import validatePricing

validated_path = validatePricing()
```

---

## Feature Engineering

### customerValueAnalyzer

#### `analyzeCustomerValue(sourcePicklePath, outputPicklePath)`

Performs RFM (Recency, Frequency, Monetary) analysis.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path

**Returns:**
- `str`: Path to RFM analysis results

**Calculated Metrics:**
- **Recency**: Days_Since_Last_Purchase
- **Frequency**: Total_Transactions, Total_Products_Purchased
- **Monetary**: Total_Spend, Average_Transaction_Value

**Example:**
```python
from modules import analyzeCustomerValue

rfm_path = analyzeCustomerValue()
```

---

### productAggregator

#### `aggregateProductData(transactionPicklePath, rfmPicklePath, outputPicklePath)`

Calculates unique product purchase metrics.

**Parameters:**
- `transactionPicklePath` (str|Path, optional): Transaction data path
- `rfmPicklePath` (str|Path, optional): RFM data path
- `outputPicklePath` (str|Path, optional): Output path

**Returns:**
- `str`: Path to aggregated dataset

**Calculated Metrics:**
- Unique_Products_Purchased

**Example:**
```python
from modules import aggregateProductData

product_path = aggregateProductData()
```

---

### behaviorAnalyzer

#### `analyzeBehaviorPatterns(transactionPicklePath, productPicklePath, outputPicklePath)`

Analyzes customer shopping behavior patterns.

**Parameters:**
- `transactionPicklePath` (str|Path, optional): Transaction data path
- `productPicklePath` (str|Path, optional): Product data path
- `outputPicklePath` (str|Path, optional): Output path

**Returns:**
- `str`: Path to behavior analysis

**Calculated Metrics:**
- Average_Days_Between_Purchases
- Day_Of_Week (favorite shopping day)
- Hour (favorite shopping hour)

**Example:**
```python
from modules import analyzeBehaviorPatterns

behavior_path = analyzeBehaviorPatterns()
```

---

### locationFeatureBuilder

#### `buildLocationFeatures(transactionPicklePath, behaviorPicklePath, outputPicklePath)`

Builds geographic features for customer analysis.

**Parameters:**
- `transactionPicklePath` (str|Path, optional): Transaction data path
- `behaviorPicklePath` (str|Path, optional): Behavior data path
- `outputPicklePath` (str|Path, optional): Output path

**Returns:**
- `str`: Path to location features

**Calculated Features:**
- Is_UK (binary: 1 if UK, 0 otherwise)

**Example:**
```python
from modules import buildLocationFeatures

location_path = buildLocationFeatures()
```

---

### cancellationAnalyzer

#### `analyzeCancellations(transactionPicklePath, locationPicklePath, outputPicklePath)`

Analyzes order cancellation patterns.

**Parameters:**
- `transactionPicklePath` (str|Path, optional): Transaction data path
- `locationPicklePath` (str|Path, optional): Location data path
- `outputPicklePath` (str|Path, optional): Output path

**Returns:**
- `str`: Path to cancellation analysis

**Calculated Metrics:**
- Cancellation_Frequency
- Cancellation_Rate

**Example:**
```python
from modules import analyzeCancellations

cancellation_path = analyzeCancellations()
```

---

### temporalPatternExtractor

#### `extractTemporalPatterns(transactionPicklePath, cancellationPicklePath, outputPicklePath)`

Extracts seasonal and temporal spending patterns.

**Parameters:**
- `transactionPicklePath` (str|Path, optional): Transaction data path
- `cancellationPicklePath` (str|Path, optional): Cancellation data path
- `outputPicklePath` (str|Path, optional): Output path

**Returns:**
- `str`: Path to temporal features

**Calculated Metrics:**
- Monthly_Spending_Mean
- Monthly_Spending_Std
- Spending_Trend (linear regression slope)

**Example:**
```python
from modules import extractTemporalPatterns

temporal_path = extractTemporalPatterns()
```

---

## Advanced Analytics

### outlierRemover

#### `removeOutliers(sourcePicklePath, outputPicklePath, contaminationRate)`

Detects and removes outlier records using Isolation Forest.

**Parameters:**
- `sourcePicklePath` (str|Path, optional): Input pickle path
- `outputPicklePath` (str|Path, optional): Output pickle path
- `contaminationRate` (float, optional): Expected outlier proportion
  - Default: 0.05 (5%)

**Returns:**
- `str`: Path to cleaned dataset

**Algorithm:**
- Isolation Forest with 100 estimators
- Random seed: 42

**Example:**
```python
from modules import removeOutliers

# Default 5% contamination
cleaned_path = removeOutliers()

# Custom contamination rate
cleaned_path = removeOutliers(contaminationRate=0.10)
```

---

## Usage Examples

### Complete Pipeline Example

```python
from modules import (
    fetchDataset,
    extractArchive,
    loadDataset,
    processMissingValues,
    eliminateDuplicates,
    classifyTransactionStatus,
    detectCodeAnomalies,
    cleanDescriptions,
    validatePricing,
    analyzeCustomerValue,
    aggregateProductData,
    analyzeBehaviorPatterns,
    buildLocationFeatures,
    analyzeCancellations,
    extractTemporalPatterns,
    removeOutliers
)

# Data Acquisition
archive_path = fetchDataset()
excel_path = extractArchive(archive_path)
data_path = loadDataset()

# Data Cleaning
step1 = processMissingValues(data_path)
step2 = eliminateDuplicates(step1)
step3 = classifyTransactionStatus(step2)
step4 = detectCodeAnomalies(step3)
step5 = cleanDescriptions(step4)
step6 = validatePricing(step5)

# Feature Engineering
rfm_path = analyzeCustomerValue(step6)
product_path = aggregateProductData(step6, rfm_path)
behavior_path = analyzeBehaviorPatterns(step6, product_path)
location_path = buildLocationFeatures(step6, behavior_path)
cancellation_path = analyzeCancellations(step6, location_path)
temporal_path = extractTemporalPatterns(step6, cancellation_path)

# Advanced Analytics
final_path = removeOutliers(temporal_path)

print(f"Pipeline complete! Final data: {final_path}")
```

### Custom Path Example

```python
from modules import loadDataset, analyzeCustomerValue
from pathlib import Path

# Custom paths
custom_data = Path("my_data/transactions.xlsx")
custom_output = Path("my_output/rfm_results.pkl")

# Load and analyze
data_path = loadDataset(excelFilePath=custom_data)
rfm_path = analyzeCustomerValue(
    sourcePicklePath=data_path,
    outputPicklePath=custom_output
)
```

---

## Error Handling

All modules follow consistent error handling patterns:

```python
try:
    result = processMissingValues()
    print(f"Success: {result}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Return Value Patterns

All processing functions return:
- **Success**: String path to output pickle file
- **Failure**: Raises appropriate exception

---

## Common Parameters

Most modules accept these standard parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `sourcePicklePath` | str\|Path | Input data file path |
| `outputPicklePath` | str\|Path | Output data file path |

Default paths follow the pattern:
```
datasets/processed/{stage_name}.pkl
```

---

## Module Dependencies

```
dataFetcher (no dependencies)
    ↓
archiveExtractor
    ↓
datasetLoader
    ↓
nullValueProcessor
    ↓
recordDeduplicator
    ↓
transactionProcessor
    ↓
codeAnomalyDetector
    ↓
descriptionCleaner
    ↓
priceValidator
    ↓
customerValueAnalyzer
    ↓
productAggregator
    ↓
behaviorAnalyzer
    ↓
locationFeatureBuilder
    ↓
cancellationAnalyzer
    ↓
temporalPatternExtractor
    ↓
outlierRemover
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0
