"""
Record Deduplicator Module

Identifies and removes duplicate transaction records based on key business columns.
Ensures data integrity for accurate customer segmentation analysis.
"""

import pickle
import os
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'cleaned_nulls.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'deduplicated_data.pkl'

# Columns used to identify duplicate records
DEDUPLICATION_COLUMNS = [
    'InvoiceNo',
    'StockCode', 
    'Description',
    'CustomerID',
    'Quantity'
]


def eliminateDuplicates(sourcePicklePath=SOURCE_PICKLE_PATH,
                       outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Remove duplicate transaction records from dataset.
    
    This function identifies and removes duplicate records based on a combination
    of invoice, product, customer, and quantity information. It preserves the
    first occurrence of each unique transaction.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where deduplicated data will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the deduplicated dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
        
    Examples
    --------
    >>> deduplicatedPath = eliminateDuplicates()
    >>> print(f"Deduplicated data saved to: {deduplicatedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("RECORD DEDUPLICATION INITIATED")
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
    
    # Display deduplication criteria
    print(f"\nDeduplication columns:")
    for column in DEDUPLICATION_COLUMNS:
        print(f"  - {column}")
    
    # Identify duplicates before removal
    duplicateMask = transactionData.duplicated(subset=DEDUPLICATION_COLUMNS, keep='first')
    duplicateCount = duplicateMask.sum()
    duplicatePercentage = (duplicateCount / initialRecordCount) * 100
    
    print(f"\nDuplicate analysis:")
    print(f"  - Duplicate records found: {duplicateCount:,} ({duplicatePercentage:.2f}%)")
    print(f"  - Unique records: {initialRecordCount - duplicateCount:,}")
    
    # Remove duplicate records (keep first occurrence)
    transactionData = transactionData.drop_duplicates(subset=DEDUPLICATION_COLUMNS, keep='first')
    
    finalRecordCount = len(transactionData)
    removedRecordCount = initialRecordCount - finalRecordCount
    
    print(f"\n✓ Removed {removedRecordCount:,} duplicate records")
    print(f"✓ Remaining unique records: {finalRecordCount:,}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save deduplicated data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ DEDUPLICATION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Deduplicated dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
