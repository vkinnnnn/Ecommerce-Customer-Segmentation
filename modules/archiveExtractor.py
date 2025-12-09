"""
Archive Extractor Module

Handles extraction of compressed dataset archives.
Supports ZIP format with error handling and validation.
"""

import zipfile
import os
from pathlib import Path


# Configure project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ARCHIVE_FILE_PATH = PROJECT_ROOT / 'datasets' / 'retail_data.zip'
EXTRACTION_DIRECTORY = PROJECT_ROOT / 'datasets'


def extractArchive(archiveFilePath=ARCHIVE_FILE_PATH, destinationDirectory=EXTRACTION_DIRECTORY):
    """
    Extract compressed dataset archive to specified directory.
    
    This function extracts ZIP archives containing the e-commerce dataset
    and validates the extraction process. It handles corrupted archives
    and provides detailed extraction feedback.
    
    Parameters
    ----------
    archiveFilePath : str or Path, optional
        Path to the ZIP archive file to extract
        Default: ARCHIVE_FILE_PATH
    destinationDirectory : str or Path, optional
        Directory where archive contents will be extracted
        Default: EXTRACTION_DIRECTORY
        
    Returns
    -------
    str
        Path to the primary extracted Excel file
        
    Raises
    ------
    FileNotFoundError
        If the archive file doesn't exist
    zipfile.BadZipFile
        If the archive is corrupted or invalid
        
    Examples
    --------
    >>> excelPath = extractArchive()
    >>> print(f"Dataset extracted to: {excelPath}")
    """
    # Convert to Path objects
    archiveFilePath = Path(archiveFilePath)
    destinationDirectory = Path(destinationDirectory)
    
    print("=" * 60)
    print("ARCHIVE EXTRACTION INITIATED")
    print("=" * 60)
    print(f"Archive: {archiveFilePath}")
    print(f"Destination: {destinationDirectory}")
    
    # Validate archive exists
    if not archiveFilePath.exists():
        errorMsg = f"Archive file not found: {archiveFilePath}"
        print(f"✗ {errorMsg}")
        raise FileNotFoundError(errorMsg)
    
    # Ensure destination directory exists
    destinationDirectory.mkdir(parents=True, exist_ok=True)
    
    try:
        # Open and extract ZIP archive
        with zipfile.ZipFile(archiveFilePath, 'r') as archiveHandle:
            # Get list of files in archive
            fileList = archiveHandle.namelist()
            print(f"\nFiles in archive: {len(fileList)}")
            for fileName in fileList:
                print(f"  - {fileName}")
            
            # Extract all contents
            print(f"\nExtracting files...")
            archiveHandle.extractall(destinationDirectory)
            
        print(f"\n{'=' * 60}")
        print("✓ EXTRACTION COMPLETED SUCCESSFULLY")
        print(f"{'=' * 60}")
        
        # Locate the primary Excel file
        excelFilePath = destinationDirectory / 'Online Retail.xlsx'
        
        if excelFilePath.exists():
            print(f"✓ Primary dataset file: {excelFilePath}")
            return str(excelFilePath)
        else:
            print(f"⚠ Warning: Expected Excel file not found")
            return str(destinationDirectory)
            
    except zipfile.BadZipFile as zipError:
        errorMsg = f"✗ Corrupted or invalid ZIP archive: {str(zipError)}"
        print(f"\n{errorMsg}")
        raise zipfile.BadZipFile(errorMsg)
        
    except Exception as genericError:
        errorMsg = f"✗ Extraction failed: {str(genericError)}"
        print(f"\n{errorMsg}")
        raise Exception(errorMsg)


if __name__ == "__main__":
    # Execute extraction when run as script
    extractedFile = extractArchive(ARCHIVE_FILE_PATH, EXTRACTION_DIRECTORY)
    print(f"\nDataset ready at: {extractedFile}")
