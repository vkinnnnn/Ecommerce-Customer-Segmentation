"""
Null Value Processor Module

Handles identification and removal of missing values in transaction datasets.
Focuses on critical columns required for customer segmentation analysis.
"""

import os
import pickle
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'transaction_data.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'cleaned_nulls.pkl'

# Critical columns that must not contain null values
CRITICAL_COLUMNS = ['CustomerID', 'Description']


def processMissingValues(sourcePicklePath=SOURCE_PICKLE_PATH, 
                         outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Remove records with missing values in critical columns.
    
    This function loads transaction data, identifies and removes records
    with null values in CustomerID and Description columns, validates
    the cleaning process, and persists the cleaned dataset.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing raw transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where cleaned data will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the cleaned dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
    ValueError
        If missing values remain after processing
        
    Examples
    --------
    >>> cleanedPath = processMissingValues()
    >>> print(f"Cleaned data saved to: {cleanedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("NULL VALUE PROCESSING INITIATED")
    print("=" * 60)
    print(f"Source: {sourcePicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data from pickle
    if not sourcePicklePath.exists():
        errorMsg = f"Source data file not found: {sourcePicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(sourcePicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} records")
    
    # Analyze missing values before cleaning
    print(f"\nMissing values analysis:")
    missingCounts = transactionData.isna().sum()
    for column, count in missingCounts[missingCounts > 0].items():
        percentage = (count / len(transactionData)) * 100
        print(f"  - {column}: {count:,} ({percentage:.2f}%)")
    
    # Remove records with null values in critical columns
    initialRecordCount = len(transactionData)
    transactionData = transactionData.dropna(subset=CRITICAL_COLUMNS)
    removedRecordCount = initialRecordCount - len(transactionData)
    
    print(f"\n✓ Removed {removedRecordCount:,} records with null critical values")
    print(f"✓ Remaining records: {len(transactionData):,}")
    
    # Validate no missing values remain
    remainingNulls = transactionData.isna().sum().sum()
    if remainingNulls != 0:
        errorMsg = (
            f"Validation failed: {remainingNulls} null values remain in dataset\n"
            f"Null distribution:\n{transactionData.isna().sum()[transactionData.isna().sum() > 0]}"
        )
        print(f"\n✗ {errorMsg}")
        raise ValueError(errorMsg)
    
    print(f"✓ Validation passed: No null values in critical columns")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ NULL VALUE PROCESSING COMPLETED")
    print(f"{'=' * 60}")
    print(f"Cleaned dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
