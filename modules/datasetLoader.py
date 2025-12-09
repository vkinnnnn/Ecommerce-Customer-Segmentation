"""
Dataset Loading Module

This module provides functionality for loading e-commerce transaction datasets
from various file formats including pickle and Excel files.
"""

import pickle
import os
from pathlib import Path
import pandas as pd


# Configure project root directory path
ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()

# Define default file paths for dataset storage
PICKLE_STORAGE_PATH = ROOT_DIRECTORY / 'datasets' / 'processed' / 'transaction_data.pkl'
EXCEL_SOURCE_PATH = ROOT_DIRECTORY / 'datasets' / 'Online Retail.xlsx'


def loadDataset(pickleFilePath=PICKLE_STORAGE_PATH, excelFilePath=EXCEL_SOURCE_PATH):
    """
    Load e-commerce transaction dataset from available sources.
    
    This function attempts to load data from a pickle file first for performance.
    If unavailable, it falls back to loading from an Excel file. The loaded data
    is automatically persisted as a pickle file for future efficient access.
    
    Parameters
    ----------
    pickleFilePath : str or Path, optional
        File path to the serialized pickle dataset
        Default: PICKLE_STORAGE_PATH
    excelFilePath : str or Path, optional
        File path to the source Excel dataset
        Default: EXCEL_SOURCE_PATH
        
    Returns
    -------
    str or Path
        Path to the persisted pickle file containing the loaded dataset
        
    Raises
    ------
    FileNotFoundError
        If neither pickle nor Excel file exists at specified paths
        
    Examples
    --------
    >>> dataPath = loadDataset()
    >>> print(f"Dataset loaded from: {dataPath}")
    """
    # Initialize dataframe container
    transactionData = None
    
    # Convert paths to Path objects for better handling
    pickleFilePath = Path(pickleFilePath)
    excelFilePath = Path(excelFilePath)
    
    # Attempt to load from pickle file (faster)
    if pickleFilePath.exists():
        with open(pickleFilePath, "rb") as fileHandle:
            transactionData = pickle.load(fileHandle)
        print(f"✓ Dataset successfully loaded from pickle: {pickleFilePath}")
        
    # Fallback to Excel file if pickle unavailable
    elif excelFilePath.exists():
        transactionData = pd.read_excel(excelFilePath, engine='openpyxl')
        print(f"✓ Dataset loaded from Excel source: {excelFilePath}")
        
    else:
        errorMessage = (
            f"Dataset not found at specified locations:\n"
            f"  - Pickle: {pickleFilePath}\n"
            f"  - Excel: {excelFilePath}"
        )
        print(f"✗ {errorMessage}")
        raise FileNotFoundError(errorMessage)
    
    # Ensure output directory exists
    pickleFilePath.parent.mkdir(parents=True, exist_ok=True)
    
    # Persist dataset as pickle for future efficient loading
    with open(pickleFilePath, "wb") as fileHandle:
        pickle.dump(transactionData, fileHandle)
    print(f"✓ Dataset persisted to: {pickleFilePath}")
    
    return str(pickleFilePath)
