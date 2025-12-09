"""
Transaction Processor Module

Classifies transactions as completed or cancelled based on invoice identifiers.
Adds transaction status metadata for business analytics.
"""

import pickle
import os
from pathlib import Path
import numpy as np


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'deduplicated_data.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'transaction_classified.pkl'


def classifyTransactionStatus(sourcePicklePath=SOURCE_PICKLE_PATH,
                              outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Add transaction status classification to dataset.
    
    This function analyzes invoice numbers to determine transaction status.
    Invoices starting with 'C' are classified as cancelled, all others as completed.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where classified data will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the classified dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
    KeyError
        If InvoiceNo column is missing from dataset
        
    Examples
    --------
    >>> classifiedPath = classifyTransactionStatus()
    >>> print(f"Classified data saved to: {classifiedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("TRANSACTION STATUS CLASSIFICATION")
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
    
    # Validate required column exists
    if 'InvoiceNo' not in transactionData.columns:
        errorMsg = "Required column 'InvoiceNo' not found in dataset"
        print(f"✗ {errorMsg}")
        raise KeyError(errorMsg)
    
    # Classify transactions based on invoice number prefix
    # Invoices starting with 'C' indicate cancellations
    transactionData['TransactionStatus'] = np.where(
        transactionData['InvoiceNo'].astype(str).str.startswith('C'),
        'Cancelled',
        'Completed'
    )
    
    # Generate classification statistics
    statusCounts = transactionData['TransactionStatus'].value_counts()
    print(f"\nTransaction classification results:")
    for status, count in statusCounts.items():
        percentage = (count / len(transactionData)) * 100
        print(f"  - {status}: {count:,} ({percentage:.2f}%)")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save classified data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ CLASSIFICATION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Classified dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
