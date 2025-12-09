"""
Product Aggregator Module

Aggregates unique product purchase data for each customer.
Calculates product diversity metrics for customer segmentation.
"""

import pickle
import os
from pathlib import Path
import pandas as pd


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRANSACTION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
RFM_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'rfm_analysis.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'product_aggregated.pkl'


def aggregateProductData(transactionPicklePath=TRANSACTION_PICKLE_PATH,
                         rfmPicklePath=RFM_PICKLE_PATH,
                         outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Calculate unique product purchase metrics for each customer.
    
    This function analyzes product diversity by counting the number of
    unique products (stock codes) purchased by each customer, providing
    insights into shopping behavior and product preferences.
    
    Parameters
    ----------
    transactionPicklePath : str or Path, optional
        Path to transaction data pickle file
        Default: TRANSACTION_PICKLE_PATH
    rfmPicklePath : str or Path, optional
        Path to RFM analysis data pickle file
        Default: RFM_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where aggregated data will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the aggregated dataset pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle files don't exist
        
    Examples
    --------
    >>> aggregatedPath = aggregateProductData()
    >>> print(f"Product aggregation saved to: {aggregatedPath}")
    """
    # Convert to Path objects
    transactionPicklePath = Path(transactionPicklePath)
    rfmPicklePath = Path(rfmPicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("PRODUCT DIVERSITY AGGREGATION")
    print("=" * 60)
    print(f"Transaction data: {transactionPicklePath}")
    print(f"RFM data: {rfmPicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data
    if not transactionPicklePath.exists():
        errorMsg = f"Transaction data file not found: {transactionPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(transactionPicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Load RFM customer data
    if not rfmPicklePath.exists():
        errorMsg = f"RFM data file not found: {rfmPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(rfmPicklePath, "rb") as fileHandle:
        customerMetrics = pickle.load(fileHandle)
    
    print(f"✓ Loaded {len(customerMetrics):,} customer records")
    
    # Calculate unique products purchased per customer
    print(f"\nCalculating product diversity metrics...")
    
    if 'CustomerID' in transactionData.columns and not transactionData.empty:
        uniqueProductsPurchased = (
            transactionData.groupby('CustomerID')['StockCode']
            .nunique()
            .reset_index()
            .rename(columns={'StockCode': 'Unique_Products_Purchased'})
        )
        
        print(f"✓ Calculated unique products for {len(uniqueProductsPurchased):,} customers")
        
        # Merge with customer metrics (only for customers in RFM data)
        customerMetrics = pd.merge(
            customerMetrics,
            uniqueProductsPurchased[
                uniqueProductsPurchased['CustomerID'].isin(customerMetrics['CustomerID'])
            ],
            on='CustomerID',
            how='left'
        )
        
        # Display product diversity statistics
        print(f"\nProduct diversity statistics:")
        print(f"  - Mean unique products: {customerMetrics['Unique_Products_Purchased'].mean():.2f}")
        print(f"  - Median unique products: {customerMetrics['Unique_Products_Purchased'].median():.2f}")
        print(f"  - Max unique products: {customerMetrics['Unique_Products_Purchased'].max():.0f}")
        print(f"  - Min unique products: {customerMetrics['Unique_Products_Purchased'].min():.0f}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save aggregated data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ PRODUCT AGGREGATION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
