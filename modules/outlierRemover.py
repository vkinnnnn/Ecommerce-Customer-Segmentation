"""
Outlier Remover Module

Detects and removes outlier records using Isolation Forest algorithm.
Improves data quality for customer segmentation modeling.
"""

import os
import pickle
from pathlib import Path
from sklearn.ensemble import IsolationForest
import numpy as np


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'temporal_features.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'outliers_removed.pkl'

# Outlier detection parameters
CONTAMINATION_RATE = 0.05  # Expected proportion of outliers (5%)
RANDOM_SEED = 42  # For reproducibility


def removeOutliers(sourcePicklePath=SOURCE_PICKLE_PATH,
                  outputPicklePath=OUTPUT_PICKLE_PATH,
                  contaminationRate=CONTAMINATION_RATE):
    """
    Detect and remove outlier records using Isolation Forest.
    
    This function applies the Isolation Forest algorithm to identify
    anomalous customer behavior patterns that could skew segmentation
    analysis. Outliers are flagged and removed from the dataset.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing feature data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where cleaned data will be saved
        Default: OUTPUT_PICKLE_PATH
    contaminationRate : float, optional
        Expected proportion of outliers in the dataset
        Default: CONTAMINATION_RATE (0.05)
        
    Returns
    -------
    str
        Path to the cleaned dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
        
    Examples
    --------
    >>> cleanedPath = removeOutliers()
    >>> print(f"Outlier-free data saved to: {cleanedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("OUTLIER DETECTION & REMOVAL")
    print("=" * 60)
    print(f"Source: {sourcePicklePath}")
    print(f"Output: {outputPicklePath}")
    print(f"Contamination rate: {contaminationRate * 100}%")
    
    # Load feature data from pickle
    if not sourcePicklePath.exists():
        errorMsg = f"Source data file not found: {sourcePicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(sourcePicklePath, "rb") as fileHandle:
        featureData = pickle.load(fileHandle)
    
    initialRecordCount = len(featureData)
    print(f"\n✓ Loaded {initialRecordCount:,} records")
    print(f"✓ Feature columns: {len(featureData.columns)}")
    
    # Initialize Isolation Forest model
    print(f"\nInitializing Isolation Forest model...")
    outlierDetector = IsolationForest(
        contamination=contaminationRate,
        random_state=RANDOM_SEED,
        n_estimators=100,
        max_samples='auto',
        verbose=0
    )
    
    # Fit model and predict outliers (excluding CustomerID column)
    print(f"Detecting outliers...")
    featureColumns = featureData.iloc[:, 1:].to_numpy()
    outlierScores = outlierDetector.fit_predict(featureColumns)
    
    # Add outlier information to dataframe
    featureData['OutlierScore'] = outlierScores
    featureData['IsOutlier'] = [1 if score == -1 else 0 for score in outlierScores]
    
    # Analyze outlier detection results
    outlierCount = featureData['IsOutlier'].sum()
    outlierPercentage = (outlierCount / initialRecordCount) * 100
    
    print(f"\nOutlier detection results:")
    print(f"  - Outliers detected: {outlierCount:,} ({outlierPercentage:.2f}%)")
    print(f"  - Normal records: {initialRecordCount - outlierCount:,}")
    
    # Remove outliers
    cleanedData = featureData[featureData['IsOutlier'] == 0].copy()
    
    # Drop temporary outlier columns
    cleanedData.drop(columns=['OutlierScore', 'IsOutlier'], inplace=True)
    
    # Reset index
    cleanedData.reset_index(drop=True, inplace=True)
    
    finalRecordCount = len(cleanedData)
    removedRecordCount = initialRecordCount - finalRecordCount
    
    print(f"\nCleaning results:")
    print(f"  - Records removed: {removedRecordCount:,}")
    print(f"  - Clean records: {finalRecordCount:,}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(cleanedData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ OUTLIER REMOVAL COMPLETED")
    print(f"{'=' * 60}")
    print(f"Cleaned dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
