# ============================================================================
# ElDawliya System - Package Installation Script for Python 3.13
# ============================================================================
# This script handles the installation of all required packages with
# special handling for packages that need compilation on Windows
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ElDawliya System - Package Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Upgrade pip, setuptools, and wheel
Write-Host "Step 1: Upgrading pip, setuptools, and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upgrade pip/setuptools/wheel" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Successfully upgraded pip, setuptools, and wheel" -ForegroundColor Green
Write-Host ""

# Install critical packages with pre-built wheels first
Write-Host "Step 2: Installing critical packages with pre-built wheels..." -ForegroundColor Yellow

# Install pyodbc (requires ODBC driver)
Write-Host "Installing pyodbc (SQL Server connector)..." -ForegroundColor Cyan
python -m pip install "pyodbc>=5.0.0" --only-binary=:all:
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Failed to install pyodbc with pre-built wheel" -ForegroundColor Yellow
    Write-Host "Attempting to install from source (requires Microsoft C++ Build Tools)..." -ForegroundColor Yellow
    python -m pip install "pyodbc>=5.0.0"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install pyodbc" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUTION: Install Microsoft C++ Build Tools" -ForegroundColor Yellow
        Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
        Write-Host "Or use: winget install Microsoft.VisualStudio.2022.BuildTools" -ForegroundColor Cyan
        Write-Host ""
        $continue = Read-Host "Continue without pyodbc? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
} else {
    Write-Host "✓ Successfully installed pyodbc" -ForegroundColor Green
}
Write-Host ""

# Install numpy first (pandas dependency)
Write-Host "Installing numpy..." -ForegroundColor Cyan
python -m pip install "numpy>=1.26.0,<2.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install numpy" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Successfully installed numpy" -ForegroundColor Green
Write-Host ""

# Install pandas
Write-Host "Installing pandas (requires numpy)..." -ForegroundColor Cyan
python -m pip install "pandas>=2.2.3"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install pandas" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Successfully installed pandas" -ForegroundColor Green
Write-Host ""

# Install matplotlib
Write-Host "Installing matplotlib..." -ForegroundColor Cyan
python -m pip install "matplotlib>=3.9.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install matplotlib" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Successfully installed matplotlib" -ForegroundColor Green
Write-Host ""

# Install all other requirements
Write-Host "Step 3: Installing remaining packages from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Some packages failed to install" -ForegroundColor Yellow
    Write-Host "Attempting to install with --no-deps flag for problematic packages..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt --no-deps
}
Write-Host ""

# Verify critical packages
Write-Host "Step 4: Verifying critical package installations..." -ForegroundColor Yellow
Write-Host ""

$packages = @(
    "django",
    "djangorestframework",
    "pyodbc",
    "pandas",
    "numpy",
    "matplotlib",
    "celery",
    "redis"
)

$failed = @()
foreach ($package in $packages) {
    $result = python -c "import $package; print($package.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $package : $result" -ForegroundColor Green
    } else {
        Write-Host "✗ $package : NOT INSTALLED" -ForegroundColor Red
        $failed += $package
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($failed.Count -eq 0) {
    Write-Host "✓ All critical packages installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: python manage.py check" -ForegroundColor Cyan
    Write-Host "2. Run: python manage.py migrate" -ForegroundColor Cyan
    Write-Host "3. Run: python manage.py test" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Some packages failed to install:" -ForegroundColor Yellow
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please check the error messages above and install missing dependencies." -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan

