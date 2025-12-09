"""
Test Suite for Data Acquisition Modules

Tests for dataFetcher, archiveExtractor, and datasetLoader modules.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pickle
import pandas as pd
from modules import fetchDataset, extractArchive, loadDataset


class TestDataFetcher:
    """Test suite for dataFetcher module."""
    
    @patch('modules.dataFetcher.requests.get')
    def test_fetch_dataset_success(self, mock_get):
        """Test successful dataset download."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content = lambda chunk_size: [b'data']
        mock_get.return_value = mock_response
        
        with patch('builtins.open', mock_open()):
            result = fetchDataset()
            assert result.endswith('.zip')
            mock_get.assert_called_once()
    
    @patch('modules.dataFetcher.requests.get')
    def test_fetch_dataset_timeout(self, mock_get):
        """Test dataset download timeout handling."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Connection timeout")
        
        with pytest.raises(Timeout):
            fetchDataset()
    
    @patch('modules.dataFetcher.requests.get')
    def test_fetch_dataset_http_error(self, mock_get):
        """Test HTTP error handling."""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("HTTP Error")
        
        with pytest.raises(RequestException):
            fetchDataset()


class TestArchiveExtractor:
    """Test suite for archiveExtractor module."""
    
    @patch('modules.archiveExtractor.zipfile.ZipFile')
    def test_extract_archive_success(self, mock_zipfile):
        """Test successful archive extraction."""
        mock_zip = Mock()
        mock_zip.namelist.return_value = ['Online Retail.xlsx']
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        with patch('pathlib.Path.exists', return_value=True):
            result = extractArchive()
            assert result.endswith('.xlsx')
    
    def test_extract_archive_file_not_found(self):
        """Test extraction with missing archive file."""
        with pytest.raises(FileNotFoundError):
            extractArchive(archiveFilePath="nonexistent.zip")
    
    @patch('modules.archiveExtractor.zipfile.ZipFile')
    def test_extract_archive_corrupted(self, mock_zipfile):
        """Test extraction of corrupted archive."""
        import zipfile
        mock_zipfile.side_effect = zipfile.BadZipFile("Corrupted archive")
        
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(zipfile.BadZipFile):
                extractArchive()


class TestDatasetLoader:
    """Test suite for datasetLoader module."""
    
    def test_load_dataset_from_pickle(self):
        """Test loading dataset from existing pickle file."""
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=test_data):
                    with patch('pickle.dump'):
                        result = loadDataset()
                        assert result.endswith('.pkl')
    
    def test_load_dataset_from_excel(self):
        """Test loading dataset from Excel when pickle doesn't exist."""
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        
        def exists_side_effect(path):
            return 'xlsx' in str(path)
        
        with patch('pathlib.Path.exists', side_effect=exists_side_effect):
            with patch('pandas.read_excel', return_value=test_data):
                with patch('builtins.open', mock_open()):
                    with patch('pickle.dump'):
                        result = loadDataset()
                        assert result.endswith('.pkl')
    
    def test_load_dataset_file_not_found(self):
        """Test loading with missing files."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                loadDataset()


# Pytest configuration
@pytest.fixture
def sample_dataframe():
    """Fixture providing sample transaction data."""
    return pd.DataFrame({
        'InvoiceNo': ['536365', '536366', 'C536367'],
        'StockCode': ['85123A', '71053', '84406B'],
        'Description': ['WHITE HANGING HEART', 'WHITE METAL LANTERN', 'CREAM CUPID HEARTS'],
        'Quantity': [6, 6, 8],
        'InvoiceDate': ['2010-12-01 08:26:00', '2010-12-01 08:28:00', '2010-12-01 08:34:00'],
        'UnitPrice': [2.55, 3.39, 2.75],
        'CustomerID': [17850.0, 17850.0, 17850.0],
        'Country': ['United Kingdom', 'United Kingdom', 'United Kingdom']
    })


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
