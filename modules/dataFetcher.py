"""
Data Fetcher Module

Handles downloading of e-commerce datasets from remote sources.
Supports HTTP/HTTPS protocols with timeout and error handling.
"""

import os
from pathlib import Path
import requests
from requests.exceptions import RequestException, Timeout


# Default UCI repository URL for online retail dataset
UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

# HTTP request configuration
REQUEST_TIMEOUT_SECONDS = 45
CHUNK_SIZE_BYTES = 8192


def fetchDataset(sourceUrl=UCI_DATASET_URL, timeoutSeconds=REQUEST_TIMEOUT_SECONDS):
    """
    Download e-commerce dataset from remote URL.
    
    This function retrieves the dataset archive from a specified URL and saves it
    to the local datasets directory. It includes progress indication and error
    handling for network issues.
    
    Parameters
    ----------
    sourceUrl : str, optional
        Remote URL of the dataset archive to download
        Default: UCI_DATASET_URL
    timeoutSeconds : int, optional
        Maximum time in seconds to wait for server response
        Default: REQUEST_TIMEOUT_SECONDS
        
    Returns
    -------
    str
        Absolute path to the downloaded archive file
        
    Raises
    ------
    RequestException
        If the HTTP request fails
    Timeout
        If the request exceeds the specified timeout
    IOError
        If file writing fails
        
    Examples
    --------
    >>> archivePath = fetchDataset()
    >>> print(f"Dataset downloaded to: {archivePath}")
    """
    print("=" * 60)
    print("DATASET DOWNLOAD INITIATED")
    print("=" * 60)
    print(f"Source URL: {sourceUrl}")
    print(f"Timeout: {timeoutSeconds}s")
    
    # Determine project root and create datasets directory
    projectRoot = Path(__file__).parent.parent.absolute()
    datasetsDirectory = projectRoot / 'datasets'
    datasetsDirectory.mkdir(parents=True, exist_ok=True)
    
    # Define destination path for downloaded archive
    archiveDestinationPath = datasetsDirectory / 'retail_data.zip'
    
    try:
        # Execute HTTP GET request with timeout
        print("\nConnecting to remote server...")
        httpResponse = requests.get(
            sourceUrl, 
            timeout=timeoutSeconds,
            stream=True
        )
        
        # Verify successful response
        httpResponse.raise_for_status()
        
        # Calculate total file size if available
        totalSize = int(httpResponse.headers.get('content-length', 0))
        
        print(f"✓ Connection established")
        if totalSize:
            print(f"✓ Dataset size: {totalSize / (1024*1024):.2f} MB")
        
        # Write content to file
        print(f"\nDownloading to: {archiveDestinationPath}")
        with open(archiveDestinationPath, "wb") as fileHandle:
            if totalSize:
                # Download with progress tracking
                downloadedBytes = 0
                for chunk in httpResponse.iter_content(chunk_size=CHUNK_SIZE_BYTES):
                    if chunk:
                        fileHandle.write(chunk)
                        downloadedBytes += len(chunk)
                        progress = (downloadedBytes / totalSize) * 100
                        print(f"\rProgress: {progress:.1f}%", end='', flush=True)
                print()  # New line after progress
            else:
                # Download without progress tracking
                fileHandle.write(httpResponse.content)
        
        print(f"\n{'=' * 60}")
        print("✓ DOWNLOAD COMPLETED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"Archive location: {archiveDestinationPath}")
        
        return str(archiveDestinationPath)
        
    except Timeout:
        errorMsg = f"✗ Download timeout after {timeoutSeconds}s"
        print(f"\n{errorMsg}")
        raise Timeout(errorMsg)
        
    except RequestException as requestError:
        errorMsg = f"✗ Download failed: {str(requestError)}"
        print(f"\n{errorMsg}")
        raise RequestException(errorMsg)
        
    except IOError as ioError:
        errorMsg = f"✗ File write error: {str(ioError)}"
        print(f"\n{errorMsg}")
        raise IOError(errorMsg)


if __name__ == "__main__":
    # Execute dataset download when run as script
    downloadedArchive = fetchDataset(UCI_DATASET_URL)
    print(f"\nDataset ready at: {downloadedArchive}")
