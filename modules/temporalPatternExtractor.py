"""
Temporal Pattern Extractor Module

Extracts seasonal and temporal spending patterns.
Calculates spending trends and variability metrics for customer segmentation.
"""

import pickle
import os
from pathlib import Path
import pandas as pd
import numpy as np
import scipy.stats as stats


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRANSACTION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
CANCELLATION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'cancellation_analyzed.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'temporal_features.pkl'


def extractTemporalPatterns(transactionPicklePath=TRANSACTION_PICKLE_PATH,
                            cancellationPicklePath=CANCELLATION_PICKLE_PATH,
                            outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Extract temporal spending patterns and seasonality trends.
    
    This function analyzes monthly spending patterns to identify seasonal
    trends, spending consistency, and growth/decline trajectories for
    each customer.
    
    Parameters
    ----------
    transactionPicklePath : str or Path, optional
        Path to transaction data pickle file
        Default: TRANSACTION_PICKLE_PATH
    cancellationPicklePath : str or Path, optional
        Path to cancellation analysis data pickle file
        Default: CANCELLATION_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where temporal features will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the temporal features pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle files don't exist
        
    Examples
    --------
    >>> temporalPath = extractTemporalPatterns()
    >>> print(f"Temporal features saved to: {temporalPath}")
    """
    # Convert to Path objects
    transactionPicklePath = Path(transactionPicklePath)
    cancellationPicklePath = Path(cancellationPicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("TEMPORAL PATTERN EXTRACTION")
    print("=" * 60)
    print(f"Transaction data: {transactionPicklePath}")
    print(f"Cancellation data: {cancellationPicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data
    if not transactionPicklePath.exists():
        errorMsg = f"Transaction data file not found: {transactionPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(transactionPicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Load cancellation customer data
    if not cancellationPicklePath.exists():
        errorMsg = f"Cancellation data file not found: {cancellationPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(cancellationPicklePath, "rb") as fileHandle:
        customerMetrics = pickle.load(fileHandle)
    
    print(f"✓ Loaded {len(customerMetrics):,} customer records")
    
    # Calculate total spend per transaction
    print(f"\nCalculating spending metrics...")
    transactionData['Total_Spend'] = transactionData['UnitPrice'] * transactionData['Quantity']
    
    # Extract temporal components
    transactionData['InvoiceDate'] = pd.to_datetime(transactionData['InvoiceDate'])
    transactionData['Year'] = transactionData['InvoiceDate'].dt.year
    transactionData['Month'] = transactionData['InvoiceDate'].dt.month
    
    # Calculate monthly spending per customer
    print(f"Analyzing monthly spending patterns...")
    monthlySpending = (
        transactionData.groupby(['CustomerID', 'Year', 'Month'])['Total_Spend']
        .sum()
        .reset_index()
    )
    
    # Calculate seasonal buying patterns (mean and std of monthly spending)
    seasonalBuyingPatterns = (
        monthlySpending.groupby('CustomerID')['Total_Spend']
        .agg(['mean', 'std'])
        .reset_index()
    )
    seasonalBuyingPatterns.rename(
        columns={
            'mean': 'Monthly_Spending_Mean',
            'std': 'Monthly_Spending_Std'
        },
        inplace=True
    )
    
    # Fill NaN standard deviations (customers with only one month of data)
    seasonalBuyingPatterns['Monthly_Spending_Std'].fillna(0, inplace=True)
    
    # Calculate spending trend using linear regression
    print(f"Calculating spending trends...")
    
    def calculateSpendingTrend(spendingTimeSeries):
        """
        Calculate spending trend slope using linear regression.
        
        Parameters
        ----------
        spendingTimeSeries : pd.Series
            Time series of spending values
            
        Returns
        -------
        float
            Slope of spending trend (positive = increasing, negative = decreasing)
        """
        if len(spendingTimeSeries) > 1:
            timePoints = np.arange(len(spendingTimeSeries))
            slope, _, _, _, _ = stats.linregress(timePoints, spendingTimeSeries)
            return slope
        return 0
    
    spendingTrends = (
        monthlySpending.groupby('CustomerID')['Total_Spend']
        .apply(calculateSpendingTrend)
        .reset_index()
    )
    spendingTrends.rename(columns={'Total_Spend': 'Spending_Trend'}, inplace=True)
    
    # Merge temporal features with customer metrics
    print(f"\nMerging temporal features...")
    customerMetrics = pd.merge(
        customerMetrics,
        seasonalBuyingPatterns,
        on='CustomerID',
        how='left'
    )
    customerMetrics = pd.merge(
        customerMetrics,
        spendingTrends,
        on='CustomerID',
        how='left'
    )
    
    # Convert CustomerID to string and optimize data types
    customerMetrics['CustomerID'] = customerMetrics['CustomerID'].astype(str)
    customerMetrics = customerMetrics.convert_dtypes()
    
    # Display temporal pattern statistics
    print(f"\nTemporal pattern statistics:")
    print(f"  - Avg monthly spending: ${seasonalBuyingPatterns['Monthly_Spending_Mean'].mean():.2f}")
    print(f"  - Avg spending variability: ${seasonalBuyingPatterns['Monthly_Spending_Std'].mean():.2f}")
    print(f"  - Customers with positive trend: {(spendingTrends['Spending_Trend'] > 0).sum():,}")
    print(f"  - Customers with negative trend: {(spendingTrends['Spending_Trend'] < 0).sum():,}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save temporal features
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ TEMPORAL PATTERN EXTRACTION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
