# Setup script to quickly initialize the virtual environment and run the server

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Run the server
Write-Host "Starting server..." -ForegroundColor Green
python app.py
