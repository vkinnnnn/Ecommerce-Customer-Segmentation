"""
Test Configuration and Fixtures

Shared test configuration, fixtures, and utilities.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


@pytest.fixture(scope='session')
def test_data_dir(tmp_path_factory):
    """Create temporary directory for test data."""
    return tmp_path_factory.mktemp('test_data')


@pytest.fixture
def sample_transaction_data():
    """
    Fixture providing comprehensive sample transaction data.
    
    Returns
    -------
    pd.DataFrame
        Sample transaction dataset with all required columns
    """
    np.random.seed(42)
    n_records = 100
    
    base_date = datetime(2011, 12, 1)
    
    return pd.DataFrame({
        'InvoiceNo': [f'53{i:04d}' if i % 10 != 0 else f'C53{i:04d}' 
                      for i in range(n_records)],
        'StockCode': np.random.choice(['85123A', '71053', '84406B', '22423'], n_records),
        'Description': np.random.choice([
            'WHITE HANGING HEART', 
            'WHITE METAL LANTERN',
            'CREAM CUPID HEARTS',
            'REGENCY CAKESTAND'
        ], n_records),
        'Quantity': np.random.randint(1, 20, n_records),
        'InvoiceDate': [base_date + timedelta(days=np.random.randint(0, 365)) 
                        for _ in range(n_records)],
        'UnitPrice': np.random.uniform(1.0, 50.0, n_records),
        'CustomerID': np.random.choice([17850, 17851, 17852, 17853], n_records),
        'Country': np.random.choice([
            'United Kingdom', 
            'France', 
            'Germany', 
            'Spain'
        ], n_records)
    })


@pytest.fixture
def sample_customer_data():
    """
    Fixture providing sample customer-level data.
    
    Returns
    -------
    pd.DataFrame
        Sample customer dataset with RFM metrics
    """
    return pd.DataFrame({
        'CustomerID': [17850, 17851, 17852],
        'Days_Since_Last_Purchase': [10, 30, 60],
        'Total_Transactions': [15, 8, 5],
        'Total_Products_Purchased': [50, 25, 15],
        'Total_Spend': [500.0, 300.0, 150.0],
        'Average_Transaction_Value': [33.33, 37.50, 30.00],
        'Unique_Products_Purchased': [10, 8, 5],
        'Average_Days_Between_Purchases': [7.5, 15.0, 30.0],
        'Day_Of_Week': [1, 3, 5],
        'Hour': [14, 10, 16],
        'Is_UK': [1, 1, 0],
        'Cancellation_Frequency': [1, 0, 2],
        'Cancellation_Rate': [0.067, 0.0, 0.4],
        'Monthly_Spending_Mean': [41.67, 37.50, 30.00],
        'Monthly_Spending_Std': [10.0, 8.0, 12.0],
        'Spending_Trend': [2.5, -1.0, 0.5]
    })


@pytest.fixture
def mock_pickle_file(tmp_path):
    """
    Create a temporary pickle file for testing.
    
    Parameters
    ----------
    tmp_path : Path
        Pytest temporary path fixture
        
    Returns
    -------
    Path
        Path to temporary pickle file
    """
    import pickle
    
    test_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    pickle_path = tmp_path / 'test_data.pkl'
    
    with open(pickle_path, 'wb') as f:
        pickle.dump(test_data, f)
    
    return pickle_path


@pytest.fixture
def mock_excel_file(tmp_path):
    """
    Create a temporary Excel file for testing.
    
    Parameters
    ----------
    tmp_path : Path
        Pytest temporary path fixture
        
    Returns
    -------
    Path
        Path to temporary Excel file
    """
    test_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    excel_path = tmp_path / 'test_data.xlsx'
    test_data.to_excel(excel_path, index=False)
    return excel_path


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for module interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time to run"
    )
    config.addinivalue_line(
        "markers", "requires_data: Tests that require dataset files"
    )


# Helper functions for tests
def assert_dataframe_equal(df1, df2, check_dtype=True):
    """
    Assert two DataFrames are equal.
    
    Parameters
    ----------
    df1 : pd.DataFrame
        First DataFrame
    df2 : pd.DataFrame
        Second DataFrame
    check_dtype : bool
        Whether to check data types
    """
    pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)


def create_test_pickle(data, path):
    """
    Create a pickle file for testing.
    
    Parameters
    ----------
    data : any
        Data to pickle
    path : Path
        Path where pickle should be saved
    """
    import pickle
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def load_test_pickle(path):
    """
    Load a pickle file for testing.
    
    Parameters
    ----------
    path : Path
        Path to pickle file
        
    Returns
    -------
    any
        Unpickled data
    """
    import pickle
    with open(path, 'rb') as f:
        return pickle.load(f)
