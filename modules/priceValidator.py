"""
Price Validator Module

Validates and filters transaction records based on unit price.
Removes records with zero or negative prices indicating data quality issues.
"""

import os
import pickle
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SOURCE_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'description_cleaned.pkl'
OUTPUT_PICKLE_PATH = PROJECT_ROOT / 'datasets' / 'processed' / 'price_validated.pkl'

# Price validation criteria
MINIMUM_VALID_PRICE = 0.01  # Minimum acceptable unit price


def validatePricing(sourcePicklePath=SOURCE_PICKLE_PATH,
                   outputPicklePath=OUTPUT_PICKLE_PATH):
    """
    Validate and filter records based on unit price.
    
    This function removes records with zero or negative unit prices,
    which indicate data quality issues, test entries, or invalid transactions.
    
    Parameters
    ----------
    sourcePicklePath : str or Path, optional
        Path to input pickle file containing transaction data
        Default: SOURCE_PICKLE_PATH
    outputPicklePath : str or Path, optional
        Path where price-validated data will be saved
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
    >>> validatedPath = validatePricing()
    >>> print(f"Price-validated data saved to: {validatedPath}")
    """
    # Convert to Path objects
    sourcePicklePath = Path(sourcePicklePath)
    outputPicklePath = Path(outputPicklePath)
    
    print("=" * 60)
    print("PRICE VALIDATION")
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
    
    # Analyze price distribution before filtering
    print(f"\nPrice distribution analysis:")
    print(f"  - Min price: ${transactionData['UnitPrice'].min():.2f}")
    print(f"  - Max price: ${transactionData['UnitPrice'].max():.2f}")
    print(f"  - Mean price: ${transactionData['UnitPrice'].mean():.2f}")
    print(f"  - Median price: ${transactionData['UnitPrice'].median():.2f}")
    
    # Count records with invalid prices
    zeroOrNegativePrices = (transactionData['UnitPrice'] <= 0).sum()
    invalidPercentage = (zeroOrNegativePrices / initialRecordCount) * 100
    
    print(f"\nInvalid price detection:")
    print(f"  - Records with price ≤ 0: {zeroOrNegativePrices:,} ({invalidPercentage:.2f}%)")
    
    # Filter records with valid prices only
    transactionData = transactionData[transactionData['UnitPrice'] > 0]
    
    finalRecordCount = len(transactionData)
    removedRecordCount = initialRecordCount - finalRecordCount
    
    print(f"\nValidation results:")
    print(f"  - Records removed: {removedRecordCount:,}")
    print(f"  - Valid records retained: {finalRecordCount:,}")
    
    # Display updated price statistics
    print(f"\nUpdated price statistics:")
    print(f"  - Min price: ${transactionData['UnitPrice'].min():.2f}")
    print(f"  - Max price: ${transactionData['UnitPrice'].max():.2f}")
    print(f"  - Mean price: ${transactionData['UnitPrice'].mean():.2f}")
    
    # Ensure output directory exists
    outputPicklePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save validated data
    with open(outputPicklePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    
    print(f"\n{'=' * 60}")
    print("✓ PRICE VALIDATION COMPLETED")
    print(f"{'=' * 60}")
    print(f"Validated dataset: {outputPicklePath}")
    
    return str(outputPicklePath)
