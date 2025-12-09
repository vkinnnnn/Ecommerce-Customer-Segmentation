"""
Description Cleaner Module

Cleans and standardizes product description text.
Removes service-related entries and normalizes text formatting.
"""

import os
import pickle
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'code_validated.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'description_cleaned.pkl'

# Service-related descriptions to exclude (not actual products)
SERVICE_DESCRIPTIONS = [
    "Next Day Carriage",
    "High Resolution Image",
    "POSTAGE",
    "Manual",
    "Discount",
    "Adjust bad debt"
]


def cleanDescriptions(sourcePicklePath=SOURCE_PICKLE_PATH,
                     outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Clean and standardize product descriptions.
    
    This function removes records with service-related descriptions that
    don't represent actual products, and standardizes all descriptions
    to uppercase for consistency.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
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
        
    Examples
    --------
    >>> cleanedPath = cleanDescriptions()
    >>> print(f"Cleaned data saved to: {cleanedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("DESCRIPTION CLEANING & STANDARDIZATION")
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
    
    # Display service descriptions to be removed
    print(f"\nService-related descriptions to exclude:")
    for desc in SERVICE_DESCRIPTIONS:
        print(f"  - {desc}")
    
    # Remove service-related descriptions
    transactionData = transactionData[
        ~transactionData['Description'].isin(SERVICE_DESCRIPTIONS)
    ]
    
    removedServiceRecords = initialRecordCount - len(transactionData)
    print(f"\n✓ Removed {removedServiceRecords:,} service-related records")
    
    # Standardize descriptions to uppercase
    print(f"✓ Standardizing descriptions to uppercase...")
    transactionData['Description'] = transactionData['Description'].str.upper()
    
    # Display sample cleaned descriptions
    sampleDescriptions = transactionData['Description'].head(5).tolist()
    print(f"\nSample standardized descriptions:")
    for idx, desc in enumerate(sampleDescriptions, 1):
        print(f"  {idx}. {desc[:60]}...")
    
    finalRecordCount = len(transactionData)
    print(f"\nFinal record count: {finalRecordCount:,}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ DESCRIPTION CLEANING COMPLETED")
    print(f"{'=' * 60}")
    print(f"Cleaned dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
