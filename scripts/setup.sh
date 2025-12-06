#!/bin/bash

# Operational Automation Tool - Setup Script

echo "=========================================="
echo "Operational Automation Tool Setup"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies (optional)
read -p "Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    pip install -r requirements-dev.txt
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data/input
mkdir -p data/output
mkdir -p data/logs

# Create .gitkeep files
touch data/input/.gitkeep
touch data/output/.gitkeep
touch data/logs/.gitkeep

# Copy configuration files
echo "Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please update with your settings"
fi

if [ ! -f config/config.yaml ]; then
    cp config/config.example.yaml config/config.yaml
    echo "Created config.yaml - please update with your settings"
fi

# Install pre-commit hooks (if dev dependencies installed)
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Installing pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Edit config/config.yaml with your settings"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the tool: python src/main.py"
echo ""
