"""
File handling utilities for reading and writing data files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file operations for various formats."""
    
    SUPPORTED_FORMATS = {
        ".csv": "csv",
        ".xlsx": "excel",
        ".xls": "excel",
        ".json": "json",
        ".parquet": "parquet",
    }
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file handler.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read file into pandas DataFrame based on extension.
        
        Args:
            file_path: Path to the file
            **kwargs: Additional arguments for pandas read functions
        
        Returns:
            DataFrame containing the data
        
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {extension}")
        
        logger.info(f"Reading file: {file_path}")
        
        try:
            if extension == ".csv":
                return pd.read_csv(path, **kwargs)
            elif extension in [".xlsx", ".xls"]:
                return pd.read_excel(path, **kwargs)
            elif extension == ".json":
                return pd.read_json(path, **kwargs)
            elif extension == ".parquet":
                return pd.read_parquet(path, **kwargs)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def write_file(
        self,
        data: pd.DataFrame,
        file_path: str,
        file_format: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Write DataFrame to file.
        
        Args:
            data: DataFrame to write
            file_path: Output file path
            file_format: Format override (csv, excel, json, parquet)
            **kwargs: Additional arguments for pandas write functions
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format
        if file_format:
            fmt = file_format.lower()
        else:
            extension = path.suffix.lower()
            fmt = self.SUPPORTED_FORMATS.get(extension, "csv")
        
        logger.info(f"Writing file: {file_path} (format: {fmt})")
        
        try:
            if fmt == "csv":
                data.to_csv(path, index=False, **kwargs)
            elif fmt == "excel":
                data.to_excel(path, index=False, **kwargs)
            elif fmt == "json":
                data.to_json(path, orient="records", **kwargs)
            elif fmt == "parquet":
                data.to_parquet(path, index=False, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {fmt}")
            
            logger.info(f"File written successfully: {file_path}")
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            raise
    
    def list_files(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """
        List files in directory matching pattern.
        
        Args:
            directory: Directory to search
            pattern: File pattern (e.g., "*.csv")
            recursive: Search recursively
        
        Returns:
            List of matching file paths
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"Directory not found: {directory}")
            return []
        
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        logger.info(f"Found {len(files)} files matching {pattern} in {directory}")
        return files
    
    def read_json_config(self, file_path: str) -> Dict[str, Any]:
        """
        Read JSON configuration file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Configuration dictionary
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {file_path}")
            return config
        except Exception as e:
            logger.error(f"Error reading config {file_path}: {str(e)}")
            raise
    
    def write_json_config(self, config: Dict[str, Any], file_path: str) -> None:
        """
        Write configuration to JSON file.
        
        Args:
            config: Configuration dictionary
            file_path: Output file path
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration written to {file_path}")
        except Exception as e:
            logger.error(f"Error writing config {file_path}: {str(e)}")
            raise
    
    def ensure_directory(self, directory: str) -> Path:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory: Directory path
        
        Returns:
            Path object for the directory
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path