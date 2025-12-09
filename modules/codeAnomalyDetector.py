"""
Code Anomaly Detector Module

Identifies and removes records with anomalous stock codes.
Filters out codes with insufficient numeric characters indicating data quality issues.
"""

import pickle
import os
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'transaction_classified.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'code_validated.pkl'

# Stock code validation criteria
MIN_NUMERIC_CHARS = 2  # Minimum numeric characters for valid stock code
EXPECTED_CODE_LENGTH_RANGE = (5, 6)  # Normal stock codes are 5-6 digits


def detectCodeAnomalies(sourcePicklePath=SOURCE_PICKLE_PATH,
                       outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Detect and remove records with anomalous stock codes.
    
    This function identifies stock codes with insufficient numeric characters
    (0 or 1 digit) which indicate data quality issues or non-product entries.
    Normal stock codes contain 5-6 numeric characters.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where validated data will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the validated dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
        
    Examples
    --------
    >>> validatedPath = detectCodeAnomalies()
    >>> print(f"Validated data saved to: {validatedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("STOCK CODE ANOMALY DETECTION")
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
    
    initialRecordCount = len(transactionData)
    print(f"\n✓ Loaded {initialRecordCount:,} records")
    
    # Identify unique stock codes
    uniqueStockCodes = transactionData['StockCode'].unique()
    print(f"✓ Found {len(uniqueStockCodes):,} unique stock codes")
    
    # Detect anomalous stock codes (0 or 1 numeric characters)
    anomalousStockCodes = [
        code for code in uniqueStockCodes
        if sum(char.isdigit() for char in str(code)) in (0, 1)
    ]
    
    print(f"\nAnomaly detection results:")
    print(f"  - Anomalous codes found: {len(anomalousStockCodes)}")
    
    if anomalousStockCodes:
        print(f"  - Sample anomalous codes: {anomalousStockCodes[:10]}")
    
    # Remove records with anomalous stock codes
    transactionData = transactionData[~transactionData['StockCode'].isin(anomalousStockCodes)]
    
    finalRecordCount = len(transactionData)
    removedRecordCount = initialRecordCount - finalRecordCount
    removalPercentage = (removedRecordCount / initialRecordCount) * 100
    
    print(f"\nCleaning results:")
    print(f"  - Records removed: {removedRecordCount:,} ({removalPercentage:.2f}%)")
    print(f"  - Records retained: {finalRecordCount:,}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save validated data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ ANOMALY DETECTION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Validated dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
