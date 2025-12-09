"""
Cancellation Analyzer Module

Analyzes order cancellation patterns and calculates cancellation metrics.
Provides insights into customer return behavior and satisfaction indicators.
"""

import pickle
import os
from pathlib import Path
import pandas as pd
import numpy as np


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRANSACTION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
LOCATION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'location_features.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'cancellation_analyzed.pkl'


def analyzeCancellations(transactionPicklePath=TRANSACTION_PICKLE_PATH,
                         locationPicklePath=LOCATION_PICKLE_PATH,
                         outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Analyze order cancellation patterns for each customer.
    
    This function calculates cancellation frequency and rates, providing
    insights into customer satisfaction, product quality issues, or
    problematic purchasing behavior.
    
    Parameters
    ----------
    transactionPicklePath : str or Path, optional
        Path to transaction data pickle file
        Default: TRANSACTION_PICKLE_PATH
    locationPicklePath : str or Path, optional
        Path to location features data pickle file
        Default: LOCATION_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where cancellation analysis will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the cancellation analysis pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle files don't exist
        
    Examples
    --------
    >>> cancellationPath = analyzeCancellations()
    >>> print(f"Cancellation analysis saved to: {cancellationPath}")
    """
    # Convert to Path objects
    transactionPicklePath = Path(transactionPicklePath)
    locationPicklePath = Path(locationPicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("CANCELLATION PATTERN ANALYSIS")
    print("=" * 60)
    print(f"Transaction data: {transactionPicklePath}")
    print(f"Location data: {locationPicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data
    if not transactionPicklePath.exists():
        errorMsg = f"Transaction data file not found: {transactionPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(transactionPicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Load location customer data
    if not locationPicklePath.exists():
        errorMsg = f"Location data file not found: {locationPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(locationPicklePath, "rb") as fileHandle:
        customerMetrics = pickle.load(fileHandle)
    
    print(f"✓ Loaded {len(customerMetrics):,} customer records")
    
    # Calculate total transactions per customer
    print(f"\nCalculating transaction metrics...")
    totalTransactions = (
        transactionData.groupby('CustomerID')['InvoiceNo']
        .nunique()
        .reset_index()
    )
    
    # Identify cancelled transactions (InvoiceNo starts with 'C')
    print(f"Identifying cancelled transactions...")
    transactionData['Transaction_Status'] = np.where(
        transactionData['InvoiceNo'].astype(str).str.startswith('C'),
        'Cancelled',
        'Completed'
    )
    
    # Analyze overall cancellation rate
    totalCancelled = (transactionData['Transaction_Status'] == 'Cancelled').sum()
    overallCancellationRate = (totalCancelled / len(transactionData)) * 100
    print(f"\nOverall cancellation statistics:")
    print(f"  - Total cancelled transactions: {totalCancelled:,} ({overallCancellationRate:.2f}%)")
    
    # Calculate cancellation frequency per customer
    cancelledTransactions = transactionData[
        transactionData['Transaction_Status'] == 'Cancelled'
    ]
    
    cancellationFrequency = (
        cancelledTransactions.groupby('CustomerID')['InvoiceNo']
        .nunique()
        .reset_index()
    )
    cancellationFrequency.rename(
        columns={'InvoiceNo': 'Cancellation_Frequency'}, 
        inplace=True
    )
    
    # Merge cancellation frequency with customer metrics
    customerMetrics = pd.merge(
        customerMetrics,
        cancellationFrequency,
        on='CustomerID',
        how='left'
    )
    
    # Fill missing values (customers with no cancellations)
    customerMetrics['Cancellation_Frequency'].fillna(0, inplace=True)
    
    # Calculate cancellation rate (cancellations / total transactions)
    customerMetrics['Cancellation_Rate'] = (
        customerMetrics['Cancellation_Frequency'] / 
        totalTransactions.set_index('CustomerID').loc[customerMetrics['CustomerID']]['InvoiceNo'].values
    )
    
    # Display cancellation statistics
    print(f"\nCustomer cancellation statistics:")
    print(f"  - Customers with cancellations: {(customerMetrics['Cancellation_Frequency'] > 0).sum():,}")
    print(f"  - Avg cancellation frequency: {customerMetrics['Cancellation_Frequency'].mean():.2f}")
    print(f"  - Avg cancellation rate: {customerMetrics['Cancellation_Rate'].mean()*100:.2f}%")
    print(f"  - Max cancellation rate: {customerMetrics['Cancellation_Rate'].max()*100:.2f}%")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save cancellation analysis
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ CANCELLATION ANALYSIS COMPLETED")
    print(f"{'=' * 60}")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
