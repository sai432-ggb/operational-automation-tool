"""
# System Architecture

## Overview

The Operational Automation Tool is designed with a modular architecture that allows for easy extension and maintenance.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Main Entry Point                     │
│                      (main.py)                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌▼──────────────┐
│ Data Cleaner │ │  Report   │ │ System Health │
│              │ │ Generator │ │   Checker     │
└───────┬──────┘ └──┬────────┘ └┬──────────────┘
        │            │            │
        └────────────┴────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌▼──────────┐
│ File Handler │ │ Validators │ │  Email    │
│              │ │            │ │ Notifier  │
└──────────────┘ └────────────┘ └───────────┘
```

## Core Components

### 1. Configuration Layer
- **Settings Management**: Centralized configuration using Pydantic
- **Environment Variables**: Support for .env files
- **YAML Configuration**: Flexible YAML-based settings

### 2. Automation Modules
- **Data Cleaner**: Handles data quality improvement
- **Report Generator**: Creates comprehensive reports
- **System Health Checker**: Monitors system resources

### 3. Utility Layer
- **File Handler**: Manages file I/O operations
- **Validators**: Data validation utilities
- **Email Notifier**: Handles notifications

### 4. Data Models
- **Pydantic Models**: Type-safe data structures
- **Dataclasses**: Simple data containers

## Data Flow

1. User initiates automation via CLI
2. Main entry point loads configuration
3. Selected modules execute sequentially
4. Results are collected and reported
5. Notifications sent if configured

## Design Patterns

- **Factory Pattern**: Object creation
- **Strategy Pattern**: Algorithm selection
- **Observer Pattern**: Event notifications
- **Singleton Pattern**: Configuration management

## Extensibility

New modules can be added by:
1. Creating a new class in `src/automation/`
2. Implementing required interfaces
3. Registering in main.py
4. Adding configuration options

## Security Considerations

- Sensitive data in environment variables
- No hardcoded credentials
- Secure file operations
- Input validation on all user data
"""

