"""
Test Suite for Feature Engineering Modules

Tests for RFM analysis, behavior analysis, and feature extraction modules.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules import (
    analyzeCustomerValue,
    aggregateProductData,
    analyzeBehaviorPatterns,
    buildLocationFeatures,
    analyzeCancellations,
    extractTemporalPatterns
)


class TestCustomerValueAnalyzer:
    """Test suite for customerValueAnalyzer module (RFM)."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data for RFM analysis."""
        base_date = datetime(2011, 12, 9)
        return pd.DataFrame({
            'CustomerID': [1, 1, 2, 2, 2],
            'InvoiceNo': ['A', 'B', 'C', 'D', 'E'],
            'InvoiceDate': [
                base_date - timedelta(days=30),
                base_date - timedelta(days=10),
                base_date - timedelta(days=5),
                base_date - timedelta(days=3),
                base_date - timedelta(days=1)
            ],
            'Quantity': [5, 3, 2, 4, 1],
            'UnitPrice': [10.0, 15.0, 20.0, 12.0, 8.0]
        })
    
    def test_analyze_customer_value(self, transaction_data):
        """Test RFM analysis calculation."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=transaction_data):
                    with patch('pickle.dump') as mock_dump:
                        result = analyzeCustomerValue()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify RFM metrics exist
                        assert 'Days_Since_Last_Purchase' in saved_data.columns
                        assert 'Total_Transactions' in saved_data.columns
                        assert 'Total_Spend' in saved_data.columns
                        assert 'Average_Transaction_Value' in saved_data.columns
                        
                        # Verify customer count
                        assert len(saved_data) == 2


class TestProductAggregator:
    """Test suite for productAggregator module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data."""
        return pd.DataFrame({
            'CustomerID': [1, 1, 1, 2, 2],
            'StockCode': ['A', 'B', 'A', 'C', 'D']
        })
    
    @pytest.fixture
    def rfm_data(self):
        """Sample RFM data."""
        return pd.DataFrame({
            'CustomerID': [1, 2],
            'Total_Spend': [100, 200]
        })
    
    def test_aggregate_product_data(self, transaction_data, rfm_data):
        """Test product aggregation."""
        def load_side_effect(file):
            if 'rfm' in str(file.name):
                return rfm_data
            return transaction_data
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', side_effect=load_side_effect):
                    with patch('pickle.dump') as mock_dump:
                        result = aggregateProductData()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify unique products calculated
                        assert 'Unique_Products_Purchased' in saved_data.columns


class TestBehaviorAnalyzer:
    """Test suite for behaviorAnalyzer module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data with temporal info."""
        return pd.DataFrame({
            'CustomerID': [1, 1, 2],
            'InvoiceDate': [
                '2011-12-01 10:00:00',
                '2011-12-05 14:00:00',
                '2011-12-03 16:00:00'
            ]
        })
    
    def test_analyze_behavior_patterns(self, transaction_data):
        """Test behavior pattern analysis."""
        product_data = pd.DataFrame({
            'CustomerID': [1, 2],
            'Total_Spend': [100, 200]
        })
        
        def load_side_effect(file):
            if 'product' in str(file.name):
                return product_data
            return transaction_data
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', side_effect=load_side_effect):
                    with patch('pickle.dump') as mock_dump:
                        result = analyzeBehaviorPatterns()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify behavioral metrics
                        assert 'Average_Days_Between_Purchases' in saved_data.columns
                        assert 'Day_Of_Week' in saved_data.columns
                        assert 'Hour' in saved_data.columns


class TestLocationFeatureBuilder:
    """Test suite for locationFeatureBuilder module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data with countries."""
        return pd.DataFrame({
            'CustomerID': [1, 1, 2, 2, 2],
            'Country': ['United Kingdom', 'United Kingdom', 'France', 'France', 'France']
        })
    
    def test_build_location_features(self, transaction_data):
        """Test location feature building."""
        behavior_data = pd.DataFrame({
            'CustomerID': [1, 2],
            'Total_Spend': [100, 200]
        })
        
        def load_side_effect(file):
            if 'behavior' in str(file.name):
                return behavior_data
            return transaction_data
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', side_effect=load_side_effect):
                    with patch('pickle.dump') as mock_dump:
                        result = buildLocationFeatures()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify location features
                        assert 'Is_UK' in saved_data.columns
                        assert saved_data.loc[saved_data['CustomerID'] == 1, 'Is_UK'].values[0] == 1
                        assert saved_data.loc[saved_data['CustomerID'] == 2, 'Is_UK'].values[0] == 0


class TestCancellationAnalyzer:
    """Test suite for cancellationAnalyzer module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data with cancellations."""
        return pd.DataFrame({
            'CustomerID': [1, 1, 1, 2, 2],
            'InvoiceNo': ['A', 'C123', 'B', 'C', 'D']
        })
    
    def test_analyze_cancellations(self, transaction_data):
        """Test cancellation analysis."""
        location_data = pd.DataFrame({
            'CustomerID': [1, 2],
            'Is_UK': [1, 0]
        })
        
        def load_side_effect(file):
            if 'location' in str(file.name):
                return location_data
            return transaction_data
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', side_effect=load_side_effect):
                    with patch('pickle.dump') as mock_dump:
                        result = analyzeCancellations()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify cancellation metrics
                        assert 'Cancellation_Frequency' in saved_data.columns
                        assert 'Cancellation_Rate' in saved_data.columns


class TestTemporalPatternExtractor:
    """Test suite for temporalPatternExtractor module."""
    
    @pytest.fixture
    def transaction_data(self):
        """Sample transaction data for temporal analysis."""
        return pd.DataFrame({
            'CustomerID': [1, 1, 1, 2, 2],
            'InvoiceDate': [
                '2011-01-01', '2011-02-01', '2011-03-01',
                '2011-01-15', '2011-02-15'
            ],
            'Quantity': [5, 3, 4, 2, 6],
            'UnitPrice': [10.0, 15.0, 12.0, 20.0, 8.0]
        })
    
    def test_extract_temporal_patterns(self, transaction_data):
        """Test temporal pattern extraction."""
        cancellation_data = pd.DataFrame({
            'CustomerID': [1, 2],
            'Cancellation_Rate': [0.1, 0.2]
        })
        
        def load_side_effect(file):
            if 'cancellation' in str(file.name):
                return cancellation_data
            return transaction_data
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', side_effect=load_side_effect):
                    with patch('pickle.dump') as mock_dump:
                        result = extractTemporalPatterns()
                        saved_data = mock_dump.call_args[0][0]
                        
                        # Verify temporal metrics
                        assert 'Monthly_Spending_Mean' in saved_data.columns
                        assert 'Monthly_Spending_Std' in saved_data.columns
                        assert 'Spending_Trend' in saved_data.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
