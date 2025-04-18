#!/bin/bash

    # init_project.sh
    # This script sets up the basic folder structure and files
    # for the VSM Mermaid Generator project.

    echo "Initializing VSM Mermaid Generator project structure..."

    # Define directory names
    PROJECT_ROOT="vsm_mermaid_generator"
    APP_DIR="${PROJECT_ROOT}/app"
    SCRIPTS_DIR="${PROJECT_ROOT}/scripts"
    DIAGRAMS_DIR="${PROJECT_ROOT}/diagrams"

    # --- Create Directories ---
    echo "Creating directories..."
    mkdir -p "${APP_DIR}"        # -p prevents errors if directory already exists
    mkdir -p "${SCRIPTS_DIR}"
    mkdir -p "${DIAGRAMS_DIR}"
    echo "Directories created: ${APP_DIR}, ${SCRIPTS_DIR}, ${DIAGRAMS_DIR}"

    # --- Create Placeholder/Core Files ---
    echo "Creating essential files..."

    # 1. Interface HTML (initially empty, user will paste code here)
    touch "${APP_DIR}/index.html"
    echo "Created empty ${APP_DIR}/index.html (Paste HTML code here)"

    # Note: The JavaScript is embedded in the HTML in this example,
    # so no separate script.js is needed initially. If you separate it later, create it here:
    # touch "${APP_DIR}/script.js"
    # echo "Created empty ${APP_DIR}/script.js (Paste JavaScript code here if separating)"

    # 2. Dockerfile for deployment (initially empty)
    touch "${APP_DIR}/Dockerfile"
    echo "Created empty ${APP_DIR}/Dockerfile (Paste Dockerfile content here)"

    # 3. Deployment script (initially empty)
    touch "${SCRIPTS_DIR}/deploy.sh"
    chmod +x "${SCRIPTS_DIR}/deploy.sh" # Make it executable
    echo "Created empty, executable ${SCRIPTS_DIR}/deploy.sh (Paste deployment script here)"

    # 4. This initialization script itself (copy it into the scripts dir for reference)
    cp "$0" "${SCRIPTS_DIR}/init_project.sh"
    echo "Copied this script to ${SCRIPTS_DIR}/init_project.sh"

    # 5. README.md file
    echo "Creating README.md..."
    cat << 'EOF' > "${PROJECT_ROOT}/README.md"
    # Value Stream Map (VSM) Mermaid Generator

    This project provides a simple web interface to generate Mermaid syntax for Value Stream Maps.

    ## Structure

    * \`/app\`: Contains the web interface (\`index.html\`) and its \`Dockerfile\`.
    * \`/diagrams\`: The recommended directory to save your generated \`.mmd\` Mermaid files.
    * \`/scripts\`: Contains helper scripts:
        * \`init_project.sh\`: Sets up this project structure (you've already run this).
        * \`deploy.sh\`: Builds and runs the web interface using Docker.
    * \`instructions.md\`: Detailed step-by-step guide on how to use this project.
    * \`README.md\`: This file.

    ## Quick Start

    1.  **Read the Instructions:** Open \`instructions.md\` for a full guide.
    2.  **Run the Interface:** Use the \`scripts/deploy.sh\` script (requires Docker).
    3.  **Generate Diagrams:** Access the interface in your browser, input your VSM steps, and copy the generated Mermaid code.
    4.  **Save & View:** Save the code into a \`.mmd\` file in the \`/diagrams\` folder and use a Mermaid viewer.

EOF
    echo "Created ${PROJECT_ROOT}/README.md"

    # 6. Instructions file (initially empty)
    touch "${PROJECT_ROOT}/instructions.md"
    echo "Created empty ${PROJECT_ROOT}/instructions.md (Paste instructions Markdown here)"

    # --- Create .gitignore (optional but good practice) ---
    echo "Creating .gitignore..."
    cat << 'EOF' > "${PROJECT_ROOT}/.gitignore"
    # Ignore OS-specific files
    .DS_Store
    Thumbs.db

    # Ignore generated diagrams (optional, depends on workflow)
    # diagrams/*.mmd

    # Add any other files/directories to ignore
EOF
    echo "Created ${PROJECT_ROOT}/.gitignore"


    echo "-----------------------------------------------------"
    echo "Project initialization complete!"
    echo "Next Steps:"
    echo "1. Navigate into the project directory: cd ${PROJECT_ROOT}"
    echo "2. Populate the following files with the code provided:"
    echo "   - ${APP_DIR}/index.html (HTML/JS Interface code)"
    echo "   - ${APP_DIR}/Dockerfile (Dockerfile content)"
    echo "   - ${SCRIPTS_DIR}/deploy.sh (Deployment script code)"
    echo "   - instructions.md (Instructions Markdown content)"
    echo "3. Follow the steps in 'instructions.md'."
    echo "-----------------------------------------------------"

    exit 0
