"""
Behavior Analyzer Module

Analyzes customer shopping behavior patterns including temporal preferences.
Calculates metrics like purchase frequency, favorite shopping times, and intervals.
"""

import pickle
import os
from pathlib import Path
import pandas as pd


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRANSACTION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
PRODUCT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'product_aggregated.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'behavior_analyzed.pkl'


def analyzeBehaviorPatterns(transactionPicklePath=TRANSACTION_PICKLE_PATH,
                            productPicklePath=PRODUCT_PICKLE_PATH,
                            outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Analyze customer shopping behavior patterns.
    
    This function extracts temporal shopping patterns including average days
    between purchases, favorite shopping day of week, and preferred shopping hour.
    These behavioral insights enhance customer segmentation accuracy.
    
    Parameters
    ----------
    transactionPicklePath : str or Path, optional
        Path to transaction data pickle file
        Default: TRANSACTION_PICKLE_PATH
    productPicklePath : str or Path, optional
        Path to product aggregated data pickle file
        Default: PRODUCT_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where behavior analysis will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the behavior analysis pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle files don't exist
        
    Examples
    --------
    >>> behaviorPath = analyzeBehaviorPatterns()
    >>> print(f"Behavior analysis saved to: {behaviorPath}")
    """
    # Convert to Path objects
    transactionPicklePath = Path(transactionPicklePath)
    productPicklePath = Path(productPicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("CUSTOMER BEHAVIOR ANALYSIS")
    print("=" * 60)
    print(f"Transaction data: {transactionPicklePath}")
    print(f"Product data: {productPicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data
    if not transactionPicklePath.exists():
        errorMsg = f"Transaction data file not found: {transactionPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(transactionPicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Load product aggregated customer data
    if not productPicklePath.exists():
        errorMsg = f"Product data file not found: {productPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(productPicklePath, "rb") as fileHandle:
        customerMetrics = pickle.load(fileHandle)
    
    print(f"✓ Loaded {len(customerMetrics):,} customer records")
    
    # Extract temporal features
    print(f"\nExtracting temporal features...")
    transactionData['InvoiceDate'] = pd.to_datetime(transactionData['InvoiceDate'])
    transactionData['InvoiceDay'] = transactionData['InvoiceDate'].dt.date
    transactionData['Day_Of_Week'] = transactionData['InvoiceDate'].dt.dayofweek
    transactionData['Hour'] = transactionData['InvoiceDate'].dt.hour
    
    # Calculate average days between purchases
    print(f"Calculating purchase intervals...")
    daysBetweenPurchases = (
        transactionData.groupby('CustomerID')['InvoiceDay']
        .apply(lambda x: (x.diff().dropna()).apply(lambda y: y.days))
    )
    
    averageDaysBetweenPurchases = (
        daysBetweenPurchases.groupby('CustomerID').mean().reset_index()
    )
    averageDaysBetweenPurchases.rename(
        columns={'InvoiceDay': 'Average_Days_Between_Purchases'}, 
        inplace=True
    )
    
    # Identify favorite shopping day of week
    print(f"Identifying shopping day preferences...")
    favoriteShoppingDay = (
        transactionData.groupby(['CustomerID', 'Day_Of_Week'])
        .size()
        .reset_index(name='Count')
    )
    favoriteShoppingDay = (
        favoriteShoppingDay.loc[
            favoriteShoppingDay.groupby('CustomerID')['Count'].idxmax()
        ][['CustomerID', 'Day_Of_Week']]
    )
    
    # Identify favorite shopping hour
    print(f"Identifying shopping hour preferences...")
    favoriteShoppingHour = (
        transactionData.groupby(['CustomerID', 'Hour'])
        .size()
        .reset_index(name='Count')
    )
    favoriteShoppingHour = (
        favoriteShoppingHour.loc[
            favoriteShoppingHour.groupby('CustomerID')['Count'].idxmax()
        ][['CustomerID', 'Hour']]
    )
    
    # Merge all behavioral metrics
    print(f"\nMerging behavioral metrics...")
    customerMetrics = pd.merge(
        customerMetrics, 
        averageDaysBetweenPurchases, 
        on='CustomerID',
        how='left'
    )
    customerMetrics = pd.merge(
        customerMetrics, 
        favoriteShoppingDay, 
        on='CustomerID',
        how='left'
    )
    customerMetrics = pd.merge(
        customerMetrics, 
        favoriteShoppingHour, 
        on='CustomerID',
        how='left'
    )
    
    # Display behavior statistics
    print(f"\nBehavior pattern statistics:")
    print(f"  - Avg days between purchases: {customerMetrics['Average_Days_Between_Purchases'].mean():.2f}")
    print(f"  - Most common shopping day: {customerMetrics['Day_Of_Week'].mode().values[0]}")
    print(f"  - Most common shopping hour: {customerMetrics['Hour'].mode().values[0]}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save behavior analysis
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ BEHAVIOR ANALYSIS COMPLETED")
    print(f"{'=' * 60}")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
