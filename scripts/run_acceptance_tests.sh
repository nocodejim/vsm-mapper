#!/bin/bash

# VSM Generator User Acceptance Test Runner
# This script sets up the environment and runs comprehensive user acceptance tests

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
VENV_DIR="$PROJECT_ROOT/.venv"
DOWNLOAD_DIR="/tmp/vsm_test_downloads"
CONTAINER_NAME="vsm-generator-test-container"
HOST_PORT=8080

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! nc -z localhost $1 2>/dev/null
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local timeout=${2:-30}
    local count=0
    
    echo_info "Waiting for service at $url to be ready..."
    
    while [ $count -lt $timeout ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo_success "Service is ready!"
            return 0
        fi
        
        count=$((count + 1))
        echo -n "."
        sleep 1
    done
    
    echo_error "Service failed to start within ${timeout} seconds"
    return 1
}

# Function to setup Python virtual environment
setup_python_env() {
    echo_info "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo_success "Created virtual environment"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    # Install required packages
    echo_info "Installing Python dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet selenium webdriver-manager
    
    echo_success "Python environment ready"
}

# Function to start the VSM application
start_application() {
    echo_info "Starting VSM Generator application..."
    
    # Check if container is already running
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo_warning "Container $CONTAINER_NAME is already running"
        return 0
    fi
    
    # Stop and remove existing container if it exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo_info "Removing existing container..."
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    
    # Check if port is available
    if ! port_available $HOST_PORT; then
        echo_error "Port $HOST_PORT is already in use"
        echo_info "Please stop the service using port $HOST_PORT or change HOST_PORT in this script"
        return 1
    fi
    
    # Start the container
    echo_info "Starting container on port $HOST_PORT..."
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "${HOST_PORT}:8080" \
        buckeye90/vsm-generator-app:latest
    
    if [ $? -eq 0 ]; then
        echo_success "Container started successfully"
        
        # Wait for the service to be ready
        if wait_for_service "http://localhost:$HOST_PORT" 30; then
            return 0
        else
            echo_error "Application failed to start properly"
            return 1
        fi
    else
        echo_error "Failed to start container"
        return 1
    fi
}

# Function to run the tests
run_tests() {
    echo_info "Running user acceptance tests..."
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Create download directory
    mkdir -p "$DOWNLOAD_DIR"
    
    # Update the download directory in the test file
    sed -i.bak "s|DOWNLOAD_DIR = \".*\"|DOWNLOAD_DIR = \"$DOWNLOAD_DIR\"|" "$PROJECT_ROOT/tests/test_user_acceptance.py"
    
    # Run the tests
    cd "$PROJECT_ROOT"
    python tests/test_user_acceptance.py
    
    local test_exit_code=$?
    
    # Restore original test file
    if [ -f "$PROJECT_ROOT/tests/test_user_acceptance.py.bak" ]; then
        mv "$PROJECT_ROOT/tests/test_user_acceptance.py.bak" "$PROJECT_ROOT/tests/test_user_acceptance.py"
    fi
    
    return $test_exit_code
}

# Function to cleanup
cleanup() {
    echo_info "Cleaning up..."
    
    # Stop and remove container
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo_info "Stopping container..."
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1
        echo_success "Container stopped and removed"
    fi
    
    # Clean up download directory
    if [ -d "$DOWNLOAD_DIR" ]; then
        echo_info "Cleaning up test downloads..."
        rm -rf "$DOWNLOAD_DIR"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --port PORT         Use custom port (default: 8080)"
    echo "  --keep-container    Don't stop container after tests"
    echo "  --headless          Run tests in headless mode"
    echo "  --setup-only        Only setup environment, don't run tests"
    echo "  --tests-only        Only run tests (assume app is already running)"
    echo ""
    echo "Examples:"
    echo "  $0                  Run full test suite"
    echo "  $0 --port 8081     Run tests on port 8081"
    echo "  $0 --setup-only    Just setup the environment"
    echo "  $0 --tests-only    Run tests against existing app"
}

# Main execution
main() {
    local keep_container=false
    local headless=false
    local setup_only=false
    local tests_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --port)
                HOST_PORT="$2"
                shift 2
                ;;
            --keep-container)
                keep_container=true
                shift
                ;;
            --headless)
                headless=true
                shift
                ;;
            --setup-only)
                setup_only=true
                shift
                ;;
            --tests-only)
                tests_only=true
                shift
                ;;
            *)
                echo_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    echo_info "VSM Generator User Acceptance Test Runner"
    echo_info "=========================================="
    
    # Check prerequisites
    echo_info "Checking prerequisites..."
    
    if ! command_exists docker; then
        echo_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists python3; then
        echo_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists curl; then
        echo_error "curl is not installed or not in PATH"
        exit 1
    fi
    
    echo_success "All prerequisites found"
    
    # Setup trap for cleanup
    if [ "$keep_container" = false ]; then
        trap cleanup EXIT
    fi
    
    # Setup Python environment
    setup_python_env
    
    if [ "$setup_only" = true ]; then
        echo_success "Environment setup completed"
        exit 0
    fi
    
    # Start application (unless tests-only mode)
    if [ "$tests_only" = false ]; then
        if ! start_application; then
            echo_error "Failed to start application"
            exit 1
        fi
    else
        echo_info "Skipping application startup (tests-only mode)"
        # Verify the application is accessible
        if ! wait_for_service "http://localhost:$HOST_PORT" 5; then
            echo_error "Application is not accessible at http://localhost:$HOST_PORT"
            echo_info "Make sure the VSM Generator is running on port $HOST_PORT"
            exit 1
        fi
    fi
    
    # Set headless mode if requested
    if [ "$headless" = true ]; then
        echo_info "Running in headless mode"
        export HEADLESS_MODE=true
    fi
    
    # Run tests
    if run_tests; then
        echo_success "All tests completed successfully!"
        
        # Show test results location
        if [ -d "$DOWNLOAD_DIR" ]; then
            echo_info "Test results and downloads available in: $DOWNLOAD_DIR"
        fi
        
        exit 0
    else
        echo_error "Some tests failed"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"