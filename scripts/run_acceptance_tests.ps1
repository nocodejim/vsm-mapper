# VSM Generator User Acceptance Test Runner (PowerShell)
# This script sets up the environment and runs comprehensive user acceptance tests

param(
    [string]$Port = "8080",
    [switch]$KeepContainer,
    [switch]$Headless,
    [switch]$SetupOnly,
    [switch]$TestsOnly,
    [switch]$Help
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$DownloadDir = "C:\temp\vsm_test_downloads"
$ContainerName = "vsm-generator-test-container"
$HostPort = $Port

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false  # Port is in use
    }
    catch {
        return $true   # Port is available
    }
}

function Wait-ForService {
    param(
        [string]$Url,
        [int]$Timeout = 30
    )
    
    Write-Info "Waiting for service at $Url to be ready..."
    
    for ($i = 0; $i -lt $Timeout; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "Service is ready!"
                return $true
            }
        }
        catch {
            # Service not ready yet
        }
        
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
    }
    
    Write-Host ""
    Write-Error "Service failed to start within $Timeout seconds"
    return $false
}

function Setup-PythonEnv {
    Write-Info "Setting up Python virtual environment..."
    
    if (-not (Test-Path $VenvDir)) {
        python -m venv $VenvDir
        Write-Success "Created virtual environment"
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    else {
        Write-Error "Failed to find activation script at $activateScript"
        return $false
    }
    
    # Install required packages
    Write-Info "Installing Python dependencies..."
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet selenium webdriver-manager
    
    Write-Success "Python environment ready"
    return $true
}

function Start-Application {
    Write-Info "Starting VSM Generator application..."
    
    # Check if container is already running
    $runningContainers = docker ps --format "table {{.Names}}" | Select-String "^$ContainerName$"
    if ($runningContainers) {
        Write-Warning "Container $ContainerName is already running"
        return $true
    }
    
    # Stop and remove existing container if it exists
    $existingContainers = docker ps -a --format "table {{.Names}}" | Select-String "^$ContainerName$"
    if ($existingContainers) {
        Write-Info "Removing existing container..."
        docker stop $ContainerName 2>$null | Out-Null
        docker rm $ContainerName 2>$null | Out-Null
    }
    
    # Check if port is available
    if (-not (Test-Port $HostPort)) {
        Write-Error "Port $HostPort is already in use"
        Write-Info "Please stop the service using port $HostPort or use -Port parameter"
        return $false
    }
    
    # Start the container
    Write-Info "Starting container on port $HostPort..."
    $result = docker run -d --name $ContainerName -p "${HostPort}:8080" buckeye90/vsm-generator-app:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container started successfully"
        
        # Wait for the service to be ready
        if (Wait-ForService "http://localhost:$HostPort" 30) {
            return $true
        }
        else {
            Write-Error "Application failed to start properly"
            return $false
        }
    }
    else {
        Write-Error "Failed to start container"
        return $false
    }
}

function Invoke-Tests {
    Write-Info "Running user acceptance tests..."
    
    # Create download directory
    if (-not (Test-Path $DownloadDir)) {
        New-Item -ItemType Directory -Path $DownloadDir -Force | Out-Null
    }
    
    # Update the download directory in the test file
    $testFile = Join-Path $ProjectRoot "tests\test_user_acceptance.py"
    $content = Get-Content $testFile -Raw
    $updatedContent = $content -replace 'DOWNLOAD_DIR = ".*"', "DOWNLOAD_DIR = `"$($DownloadDir.Replace('\', '/'))`""
    Set-Content -Path $testFile -Value $updatedContent
    
    # Set headless mode if requested
    if ($Headless) {
        $env:HEADLESS_MODE = "true"
    }
    
    # Run the tests
    Set-Location $ProjectRoot
    python tests\test_user_acceptance.py
    
    return $LASTEXITCODE -eq 0
}

function Stop-Application {
    Write-Info "Cleaning up..."
    
    # Stop and remove container
    $runningContainers = docker ps --format "table {{.Names}}" | Select-String "^$ContainerName$"
    if ($runningContainers) {
        Write-Info "Stopping container..."
        docker stop $ContainerName 2>$null | Out-Null
        docker rm $ContainerName 2>$null | Out-Null
        Write-Success "Container stopped and removed"
    }
    
    # Clean up download directory
    if (Test-Path $DownloadDir) {
        Write-Info "Cleaning up test downloads..."
        Remove-Item -Path $DownloadDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Show-Usage {
    Write-Host "Usage: .\run_acceptance_tests.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Port PORT          Use custom port (default: 8080)"
    Write-Host "  -KeepContainer      Don't stop container after tests"
    Write-Host "  -Headless           Run tests in headless mode"
    Write-Host "  -SetupOnly          Only setup environment, don't run tests"
    Write-Host "  -TestsOnly          Only run tests (assume app is already running)"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_acceptance_tests.ps1                Run full test suite"
    Write-Host "  .\run_acceptance_tests.ps1 -Port 8081     Run tests on port 8081"
    Write-Host "  .\run_acceptance_tests.ps1 -SetupOnly     Just setup the environment"
    Write-Host "  .\run_acceptance_tests.ps1 -TestsOnly     Run tests against existing app"
}

# Main execution
function Main {
    if ($Help) {
        Show-Usage
        exit 0
    }
    
    Write-Info "VSM Generator User Acceptance Test Runner"
    Write-Info "=========================================="
    
    # Check prerequisites
    Write-Info "Checking prerequisites..."
    
    if (-not (Test-Command "docker")) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    if (-not (Test-Command "python")) {
        Write-Error "Python is not installed or not in PATH"
        exit 1
    }
    
    Write-Success "All prerequisites found"
    
    # Setup cleanup if not keeping container
    if (-not $KeepContainer) {
        Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
            Stop-Application
        } | Out-Null
    }
    
    # Setup Python environment
    if (-not (Setup-PythonEnv)) {
        Write-Error "Failed to setup Python environment"
        exit 1
    }
    
    if ($SetupOnly) {
        Write-Success "Environment setup completed"
        exit 0
    }
    
    # Start application (unless tests-only mode)
    if (-not $TestsOnly) {
        if (-not (Start-Application)) {
            Write-Error "Failed to start application"
            exit 1
        }
    }
    else {
        Write-Info "Skipping application startup (tests-only mode)"
        # Verify the application is accessible
        if (-not (Wait-ForService "http://localhost:$HostPort" 5)) {
            Write-Error "Application is not accessible at http://localhost:$HostPort"
            Write-Info "Make sure the VSM Generator is running on port $HostPort"
            exit 1
        }
    }
    
    # Run tests
    if (Invoke-Tests) {
        Write-Success "All tests completed successfully!"
        
        # Show test results location
        if (Test-Path $DownloadDir) {
            Write-Info "Test results and downloads available in: $DownloadDir"
        }
        
        exit 0
    }
    else {
        Write-Error "Some tests failed"
        exit 1
    }
}

# Execute main function
try {
    Main
}
finally {
    if (-not $KeepContainer) {
        Stop-Application
    }
}