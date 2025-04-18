    # deploy.sh
    # Located in: vsm_mermaid_generator/scripts/deploy.sh
    # This script builds the Docker image for the VSM generator web app
    # and runs it in a container.

    # --- Configuration ---
    IMAGE_NAME="vsm-generator-app"
    CONTAINER_NAME="vsm-generator-container"
    APP_PORT=8080 # Port inside the container the app runs on (defined in Dockerfile)
    HOST_PORT=8080 # Port on your local machine to access the app

    # --- Script Logic ---
    echo "Starting deployment process for VSM Generator..."

    # 1. Navigate to the app directory relative to the script's location
    # This ensures the Docker build context is correct.
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    APP_DIR="$SCRIPT_DIR/../app" # Go up one level from scripts, then into app

    if [ ! -d "$APP_DIR" ]; then
        echo "Error: App directory not found at expected location: $APP_DIR"
        exit 1
    fi

    cd "$APP_DIR"
    echo "Changed directory to: $(pwd)" # Should be the 'app' directory

    # Check if Dockerfile exists
    if [ ! -f "Dockerfile" ]; then
        echo "Error: Dockerfile not found in $(pwd)."
        echo "Make sure you have copied the Dockerfile content into app/Dockerfile."
        exit 1
    fi

    # 2. Build the Docker image
    echo "Building Docker image '$IMAGE_NAME'..."
    docker build -t "$IMAGE_NAME" .
    # The '.' means use the current directory (APP_DIR) as the build context.
    # -t tags the image with the name specified.

    if [ $? -ne 0 ]; then
        echo "Error: Docker image build failed."
        exit 1
    fi
    echo "Docker image built successfully."

    # 3. Stop and remove any existing container with the same name (optional, prevents conflicts)
    echo "Checking for existing container '$CONTAINER_NAME'..."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Stopping existing container..."
        docker stop "$CONTAINER_NAME"
    fi
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        echo "Removing existing container..."
        docker rm "$CONTAINER_NAME"
    fi

    # 4. Run the Docker container
    echo "Running Docker container '$CONTAINER_NAME'..."
    docker run \
        -d \
        --name "$CONTAINER_NAME" \
        -p "${HOST_PORT}:${APP_PORT}" \
        "$IMAGE_NAME"
    # -d: Run in detached mode (in the background)
    # --name: Assign a name to the container
    # -p: Map host port to container port (HOST_PORT:APP_PORT)

    if [ $? -ne 0 ]; then
        echo "Error: Failed to run Docker container."
        exit 1
    fi

    echo "-----------------------------------------------------"
    echo "VSM Generator App Deployment Complete!"
    echo "Access the web interface at: http://localhost:${HOST_PORT}"
    echo "To stop the container, run: docker stop ${CONTAINER_NAME}"
    echo "To remove the container (after stopping), run: docker rm ${CONTAINER_NAME}"
    echo "-----------------------------------------------------"

    # Return to the original directory (optional)
    # cd - > /dev/null

    exit 0