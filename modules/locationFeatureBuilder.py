"""
Location Feature Builder Module

Builds geographic features for customer segmentation.
Identifies primary customer location and creates regional indicators.
"""

import pickle
import os
from pathlib import Path
import pandas as pd


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TRANSACTION_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'
BEHAVIOR_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'behavior_analyzed.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'location_features.pkl'


def buildLocationFeatures(transactionPicklePath=TRANSACTION_PICKLE_PATH,
                          behaviorPicklePath=BEHAVIOR_PICKLE_PATH,
                          outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Build geographic features for customer analysis.
    
    This function identifies each customer's primary country based on
    transaction frequency and creates binary indicators for key regions
    (e.g., UK vs international customers).
    
    Parameters
    ----------
    transactionPicklePath : str or Path, optional
        Path to transaction data pickle file
        Default: TRANSACTION_PICKLE_PATH
    behaviorPicklePath : str or Path, optional
        Path to behavior analysis data pickle file
        Default: BEHAVIOR_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where location features will be saved
        Default: OUTPUT_PICKLE_PATH
        
    Returns
    -------
    str
        Path to the location features pickle file
        
    Raises
    ------
    FileNotFoundError
        If source pickle files don't exist
        
    Examples
    --------
    >>> locationPath = buildLocationFeatures()
    >>> print(f"Location features saved to: {locationPath}")
    """
    # Convert to Path objects
    transactionPicklePath = Path(transactionPicklePath)
    behaviorPicklePath = Path(behaviorPicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("GEOGRAPHIC FEATURE ENGINEERING")
    print("=" * 60)
    print(f"Transaction data: {transactionPicklePath}")
    print(f"Behavior data: {behaviorPicklePath}")
    print(f"Output: {outputPicklePath}")
    
    # Load transaction data
    if not transactionPicklePath.exists():
        errorMsg = f"Transaction data file not found: {transactionPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(transactionPicklePath, "rb") as fileHandle:
        transactionData = pickle.load(fileHandle)
    
    print(f"\n✓ Loaded {len(transactionData):,} transaction records")
    
    # Load behavior customer data
    if not behaviorPicklePath.exists():
        errorMsg = f"Behavior data file not found: {behaviorPicklePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    with open(behaviorPicklePath, "rb") as fileHandle:
        customerMetrics = pickle.load(fileHandle)
    
    print(f"✓ Loaded {len(customerMetrics):,} customer records")
    
    # Analyze country distribution
    print(f"\nAnalyzing geographic distribution...")
    countryDistribution = transactionData['Country'].value_counts(normalize=True).head(10)
    print(f"\nTop 10 countries by transaction volume:")
    for country, percentage in countryDistribution.items():
        print(f"  - {country}: {percentage*100:.2f}%")
    
    # Identify customer's primary country
    print(f"\nIdentifying primary customer locations...")
    customerCountry = (
        transactionData.groupby(['CustomerID', 'Country'])
        .size()
        .reset_index(name='Number_of_Transactions')
    )
    
    # Get country with most transactions for each customer
    customerMainCountry = (
        customerCountry.sort_values('Number_of_Transactions', ascending=False)
        .drop_duplicates('CustomerID')
    )
    
    # Create UK indicator (binary feature)
    customerMainCountry['Is_UK'] = (
        customerMainCountry['Country'].apply(
            lambda x: 1 if x == 'United Kingdom' else 0
        )
    )
    
    # Calculate UK customer percentage
    ukPercentage = (customerMainCountry['Is_UK'].sum() / len(customerMainCountry)) * 100
    print(f"\nGeographic distribution:")
    print(f"  - UK customers: {customerMainCountry['Is_UK'].sum():,} ({ukPercentage:.2f}%)")
    print(f"  - International customers: {(~customerMainCountry['Is_UK'].astype(bool)).sum():,} ({100-ukPercentage:.2f}%)")
    
    # Merge location features with customer metrics
    customerMetrics = pd.merge(
        customerMetrics,
        customerMainCountry[['CustomerID', 'Is_UK']],
        on='CustomerID',
        how='left'
    )
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save location features
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(customerMetrics, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ LOCATION FEATURE ENGINEERING COMPLETED")
    print(f"{'=' * 60}")
    print(f"Output: {outputPicklePath}")
    
    return str(outputPicklePath)
