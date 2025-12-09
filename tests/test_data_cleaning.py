"""
Test Suite for Data Cleaning Modules

Tests for data cleaning and validation modules.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pickle
import pandas as pd
import numpy as np
from modules import (
    processMissingValues,
    eliminateDuplicates,
    classifyTransactionStatus,
    detectCodeAnomalies,
    cleanDescriptions,
    validatePricing
)


class TestNullValueProcessor:
    """Test suite for nullValueProcessor module."""
    
    @pytest.fixture
    def data_with_nulls(self):
        """Sample data with missing values."""
        return pd.DataFrame({
            'CustomerID': [1.0, 2.0, np.nan, 4.0],
            'Description': ['Item A', 'Item B', 'Item C', np.nan],
            'Quantity': [1, 2, 3, 4]
        })
    
    def test_process_missing_values_success(self, data_with_nulls):
        """Test successful null value processing."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_nulls):
                    with patch('pickle.dump') as mock_dump:
                        result = processMissingValues()
                        assert result.endswith('.pkl')
                        # Verify data was cleaned
                        saved_data = mock_dump.call_args[0][0]
                        assert saved_data['CustomerID'].isna().sum() == 0
    
    def test_process_missing_values_validation_error(self):
        """Test validation error when nulls remain."""
        data_with_remaining_nulls = pd.DataFrame({
            'CustomerID': [1.0, 2.0, 3.0],
            'Description': ['A', 'B', 'C'],
            'OtherCol': [1, np.nan, 3]
        })
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_remaining_nulls):
                    with pytest.raises(ValueError, match="null values remain"):
                        processMissingValues()


class TestRecordDeduplicator:
    """Test suite for recordDeduplicator module."""
    
    @pytest.fixture
    def data_with_duplicates(self):
        """Sample data with duplicate records."""
        return pd.DataFrame({
            'InvoiceNo': ['A', 'A', 'B'],
            'StockCode': ['X', 'X', 'Y'],
            'Description': ['Item', 'Item', 'Item2'],
            'CustomerID': [1, 1, 2],
            'Quantity': [5, 5, 3]
        })
    
    def test_eliminate_duplicates_success(self, data_with_duplicates):
        """Test successful duplicate removal."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_duplicates):
                    with patch('pickle.dump') as mock_dump:
                        result = eliminateDuplicates()
                        assert result.endswith('.pkl')
                        # Verify duplicates removed
                        saved_data = mock_dump.call_args[0][0]
                        assert len(saved_data) == 2


class TestTransactionProcessor:
    """Test suite for transactionProcessor module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data."""
        return pd.DataFrame({
            'InvoiceNo': ['536365', 'C536366', '536367'],
            'CustomerID': [1, 2, 3]
        })
    
    def test_classify_transaction_status(self, transaction_data):
        """Test transaction status classification."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=transaction_data):
                    with patch('pickle.dump') as mock_dump:
                        result = classifyTransactionStatus()
                        saved_data = mock_dump.call_args[0][0]
                        assert 'TransactionStatus' in saved_data.columns
                        assert saved_data.iloc[0]['TransactionStatus'] == 'Completed'
                        assert saved_data.iloc[1]['TransactionStatus'] == 'Cancelled'


class TestCodeAnomalyDetector:
    """Test suite for codeAnomalyDetector module."""
    
    @pytest.fixture
    def data_with_anomalies(self):
        """Sample data with anomalous stock codes."""
        return pd.DataFrame({
            'StockCode': ['85123A', 'M', 'POST', '71053', 'D'],
            'CustomerID': [1, 2, 3, 4, 5]
        })
    
    def test_detect_code_anomalies(self, data_with_anomalies):
        """Test anomalous code detection."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_anomalies):
                    with patch('pickle.dump') as mock_dump:
                        result = detectCodeAnomalies()
                        saved_data = mock_dump.call_args[0][0]
                        # Should remove codes with 0-1 digits
                        assert len(saved_data) == 2  # Only valid codes remain


class TestDescriptionCleaner:
    """Test suite for descriptionCleaner module."""
    
    @pytest.fixture
    def data_with_services(self):
        """Sample data with service descriptions."""
        return pd.DataFrame({
            'Description': ['white mug', 'Next Day Carriage', 'blue plate', 'POSTAGE'],
            'CustomerID': [1, 2, 3, 4]
        })
    
    def test_clean_descriptions(self, data_with_services):
        """Test description cleaning."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_services):
                    with patch('pickle.dump') as mock_dump:
                        result = cleanDescriptions()
                        saved_data = mock_dump.call_args[0][0]
                        # Should remove service descriptions
                        assert len(saved_data) == 2
                        # Should uppercase descriptions
                        assert all(saved_data['Description'].str.isupper())


class TestPriceValidator:
    """Test suite for priceValidator module."""
    
    @pytest.fixture
    def data_with_invalid_prices(self):
        """Sample data with invalid prices."""
        return pd.DataFrame({
            'UnitPrice': [2.50, 0.0, -1.0, 3.99, 0],
            'CustomerID': [1, 2, 3, 4, 5]
        })
    
    def test_validate_pricing(self, data_with_invalid_prices):
        """Test price validation."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=data_with_invalid_prices):
                    with patch('pickle.dump') as mock_dump:
                        result = validatePricing()
                        saved_data = mock_dump.call_args[0][0]
                        # Should remove zero and negative prices
                        assert len(saved_data) == 2
                        assert all(saved_data['UnitPrice'] > 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
