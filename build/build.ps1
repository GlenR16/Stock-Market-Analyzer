$ErrorActionPreference = "SilentlyContinue"


# Store the current working directory
Write-Host "Getting current location..." -ForegroundColor Green
$root = Get-Location


# Create python virtual environment if it doesn't exist
if (!(Test-Path $root\venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv $root\venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
. $root\venv\Scripts\Activate.ps1

# Install python dependencies
Write-Host "Installing python dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet --log-file ./logs/pip.log

# Setup directory structure for docker compose silently
Write-Host "Setting up directory structure for docker compose..." -ForegroundColor Green

New-Item -ItemType Directory -Path $root\docker
New-Item -ItemType Directory -Path $root\docker\postgres
New-Item -ItemType Directory -Path $root\docker\postgres\logs
New-Item -ItemType Directory -Path $root\docker\postgres\data


# Start docker containers
Write-Host "Starting docker containers..." -ForegroundColor Green

$ErrorActionPreference = "Continue"
docker-compose --env-file .production.env up