#!/bin/bash

# setup_test_env.sh
# This script automates the setup of the Python testing environment
# for the VSM Generator UI tests.
# It creates a virtual environment, installs dependencies, and checks prerequisites.
# Run this script from the project root directory (vsm_mermaid_generator).

echo "--- VSM Generator Test Environment Setup ---"

# --- Configuration ---
VENV_DIR=".venv" # Name of the virtual environment directory
TESTS_DIR="tests" # Expected directory for test scripts
REQ_FILE="${TESTS_DIR}/requirements.txt" # Optional requirements file
PYTHON_CMD="python3" # Command to use for Python 3 (change to 'python' if needed)

# --- Helper Functions ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_error() {
    if [ $? -ne 0 ]; then
        echo "[ERROR] $1"
        exit 1
    fi
}

# --- Prerequisite Checks ---
echo "[1/5] Checking prerequisites..."

# Check for Python 3
if ! command_exists $PYTHON_CMD; then
    echo "[ERROR] $PYTHON_CMD command not found. Please install Python 3."
    exit 1
fi
echo "  - Python 3 found ($($PYTHON_CMD --version))"

# Check if running from project root (simple check for 'app' dir)
if [ ! -d "app" ]; then
    echo "[ERROR] Please run this script from the project root directory (e.g., 'vsm_mermaid_generator')."
    exit 1
fi
echo "  - Running from project root."

# Check/Create tests directory
if [ ! -d "$TESTS_DIR" ]; then
    echo "  - Creating directory for tests: $TESTS_DIR"
    mkdir "$TESTS_DIR"
    check_error "Failed to create $TESTS_DIR directory."
else
    echo "  - Tests directory found: $TESTS_DIR"
fi

# Reminder for the test script file
if [ ! -f "${TESTS_DIR}/test_vsm_generator.py" ]; then
     echo "[WARNING] Test script '${TESTS_DIR}/test_vsm_generator.py' not found."
     echo "          Please ensure you save the Python test script in the '$TESTS_DIR' directory."
fi

# --- Virtual Environment Setup ---
echo "[2/5] Setting up Python virtual environment ('$VENV_DIR')..."

if [ ! -d "$VENV_DIR" ]; then
    echo "  - Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
    check_error "Failed to create virtual environment."
    echo "  - Virtual environment created."
else
    echo "  - Virtual environment already exists."
fi

# Determine the correct pip executable path based on OS
PIP_CMD=""
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    PIP_CMD="$VENV_DIR/bin/pip"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Check for both .exe and without extension for different Windows environments
    if [ -f "$VENV_DIR/Scripts/pip.exe" ]; then
        PIP_CMD="$VENV_DIR/Scripts/pip.exe"
    elif [ -f "$VENV_DIR/Scripts/pip" ]; then
         PIP_CMD="$VENV_DIR/Scripts/pip"
    fi
else
    echo "[WARNING] Unrecognized OS type '$OSTYPE'. Attempting standard pip path."
    PIP_CMD="$VENV_DIR/bin/pip" # Default guess
fi

if [ -z "$PIP_CMD" ] || [ ! -f "$PIP_CMD" ]; then
    echo "[ERROR] Could not find pip executable in the virtual environment '$VENV_DIR'."
    echo "        Expected paths like '$VENV_DIR/bin/pip' (Linux/macOS) or '$VENV_DIR/Scripts/pip.exe' (Windows)."
    exit 1
fi
echo "  - Found pip executable: $PIP_CMD"


# --- Install Dependencies ---
echo "[3/5] Installing/Updating Python dependencies..."

# Define dependencies directly here or use a requirements file
# Using direct definition for simplicity in this case
echo "  - Installing selenium and webdriver-manager..."
"$PIP_CMD" install selenium webdriver-manager
check_error "Failed to install Python dependencies."
echo "  - Dependencies installed successfully."

# Optional: Create/Update requirements.txt
# echo "  - Generating ${REQ_FILE}..."
# "$PIP_CMD" freeze > "$REQ_FILE"

# --- .gitignore Setup ---
echo "[4/5] Checking .gitignore for '$VENV_DIR'..."
GITIGNORE_FILE=".gitignore"
if [ ! -f "$GITIGNORE_FILE" ]; then
    echo "  - Creating $GITIGNORE_FILE..."
    echo "# Ignore Python virtual environment" > "$GITIGNORE_FILE"
    echo "$VENV_DIR/" >> "$GITIGNORE_FILE"
    echo "# Ignore OS-specific files" >> "$GITIGNORE_FILE"
    echo ".DS_Store" >> "$GITIGNORE_FILE"
    echo "Thumbs.db" >> "$GITIGNORE_FILE"
    echo "# Ignore test download directory (if created)" >> "$GITIGNORE_FILE"
    echo "vsm_test_downloads/" >> "$GITIGNORE_FILE" # Add placeholder if user uses this name
    check_error "Failed to create $GITIGNORE_FILE."
    echo "  - $GITIGNORE_FILE created and '$VENV_DIR/' added."
else
    if grep -q "^${VENV_DIR}/$" "$GITIGNORE_FILE"; then
        echo "  - '$VENV_DIR/' already present in $GITIGNORE_FILE."
    else
        echo "  - Adding '$VENV_DIR/' to $GITIGNORE_FILE..."
        echo "" >> "$GITIGNORE_FILE" # Add newline for separation
        echo "# Ignore Python virtual environment" >> "$GITIGNORE_FILE"
        echo "$VENV_DIR/" >> "$GITIGNORE_FILE"
        check_error "Failed to add '$VENV_DIR/' to $GITIGNORE_FILE."
        echo "  - '$VENV_DIR/' added."
    fi
fi

# --- Final Instructions ---
echo "[5/5] Setup complete!"
echo ""
echo "--- NEXT STEPS ---"
echo "1. Ensure the test script '${TESTS_DIR}/test_vsm_generator.py' exists."
echo "2. **CRITICAL:** Edit '${TESTS_DIR}/test_vsm_generator.py' and set the 'DOWNLOAD_DIR' variable"
echo "   to an appropriate absolute path for your system."
echo "3. Activate the virtual environment in your terminal:"
echo "   - macOS/Linux: source $VENV_DIR/bin/activate"
echo "   - Windows CMD:   .\\${VENV_DIR}\\Scripts\\activate.bat"
echo "   - Windows PowerShell: .\\${VENV_DIR}\\Scripts\\Activate.ps1"
echo "4. Ensure the VSM Docker container is running (e.g., use 'scripts/deploy.sh')."
echo "5. Run the test from the project root directory:"
echo "   python ${TESTS_DIR}/test_vsm_generator.py"
echo "6. When finished, deactivate the environment by typing: deactivate"
echo "------------------"

exit 0
