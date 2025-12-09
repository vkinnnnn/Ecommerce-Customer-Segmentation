"""
Customer Value Analyzer Module

Implements RFM (Recency, Frequency, Monetary) analysis for customer segmentation.
Calculates key metrics to evaluate customer value and behavior patterns.
"""

import pickle
import os
from pathlib import Path
import pandas as pd


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'rfm_analysis.pkl'


def analyzeCustomerValue(sourcePicklePath=SOURCE_PICKLE_PATH,
                        outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Perform RFM analysis on customer transaction data.
    
    This function calculates Recency (days since last purchase), Frequency
    (number of transactions), and Monetary (total spend) metrics for each
    customer to enable value-based segmentation.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where RFM analysis results will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the RFM analysis results pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle file doesn't exist
        
    Examples
    --------
    >>> rfmPath = analyzeCustomerValue()
    >>> print(f"RFM analysis saved to: {rfmPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("RFM CUSTOMER VALUE ANALYSIS")
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
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Convert InvoiceDate to datetime and extract date component
    transactionData['InvoiceDate'] = pd.to_datetime(transactionData['InvoiceDate'])
    transactionData['InvoiceDay'] = transactionData['InvoiceDate'].dt.date
    
    # Calculate Recency: Days since last purchase
    print("\nCalculating Recency metrics...")
    customerLastPurchase = transactionData.groupby('CustomerID')['InvoiceDay'].max().reset_index()
    mostRecentDate = transactionData['InvoiceDay'].max()
    
    customerLastPurchase['InvoiceDay'] = pd.to_datetime(customerLastPurchase['InvoiceDay'])
    mostRecentDate = pd.to_datetime(mostRecentDate)
    
    customerLastPurchase['Days_Since_Last_Purchase'] = (
        (mostRecentDate - customerLastPurchase['InvoiceDay']).dt.days
    )
    customerLastPurchase.drop(columns=['InvoiceDay'], inplace=True)
    
    # Calculate Frequency: Number of unique transactions
    print("Calculating Frequency metrics...")
    totalTransactions = transactionData.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
    totalTransactions.rename(columns={'InvoiceNo': 'Total_Transactions'}, inplace=True)
    
    # Calculate total products purchased
    totalProductsPurchased = transactionData.groupby('CustomerID')['Quantity'].sum().reset_index()
    totalProductsPurchased.rename(columns={'Quantity': 'Total_Products_Purchased'}, inplace=True)
    
    # Merge frequency metrics
    customerMetrics = pd.merge(customerLastPurchase, totalTransactions, on='CustomerID')
    customerMetrics = pd.merge(customerMetrics, totalProductsPurchased, on='CustomerID')
    
    # Calculate Monetary: Total spend and average transaction value
    print("Calculating Monetary metrics...")
    transactionData['Total_Spend'] = transactionData['UnitPrice'] * transactionData['Quantity']
    totalSpend = transactionData.groupby('CustomerID')['Total_Spend'].sum().reset_index()
    
    averageTransactionValue = totalSpend.merge(totalTransactions, on='CustomerID')
    averageTransactionValue['Average_Transaction_Value'] = (
        averageTransactionValue['Total_Spend'] / averageTransactionValue['Total_Transactions']
    )
    
    # Merge monetary metrics
    customerMetrics = pd.merge(customerMetrics, totalSpend, on='CustomerID')
    customerMetrics = pd.merge(
        customerMetrics,
        averageTransactionValue[['CustomerID', 'Average_Transaction_Value']],
        on='CustomerID'
    )
    
    # Display RFM summary statistics
    print(f"\n{'=' * 60}")
    print("RFM ANALYSIS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total unique customers: {len(customerMetrics):,}")
    print(f"\nRecency (Days Since Last Purchase):")
    print(f"  - Mean: {customerMetrics['Days_Since_Last_Purchase'].mean():.2f} days")
    print(f"  - Median: {customerMetrics['Days_Since_Last_Purchase'].median():.2f} days")
    print(f"\nFrequency (Total Transactions):")
    print(f"  - Mean: {customerMetrics['Total_Transactions'].mean():.2f}")
    print(f"  - Median: {customerMetrics['Total_Transactions'].median():.2f}")
    print(f"\nMonetary (Total Spend):")
    print(f"  - Mean: ${customerMetrics['Total_Spend'].mean():.2f}")
    print(f"  - Median: ${customerMetrics['Total_Spend'].median():.2f}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save RFM analysis results
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n✓ RFM analysis completed and saved")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
