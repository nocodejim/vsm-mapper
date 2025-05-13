    # Using the Value Stream Map (VSM) Mermaid Generator

    This guide explains how to run and use the VSM Mermaid Generator application using its pre-built Docker container. This tool provides a simple web interface to help you create Value Stream Map diagrams using Mermaid syntax.

    ## 1. Prerequisites

    * **Docker:** You need Docker installed and running on your computer. If you don't have it, download and install Docker Desktop from the official Docker website: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    * **Terminal/Command Line:** You'll need a terminal or command prompt to run the Docker command.
        * **Windows:** Command Prompt, PowerShell, or Git Bash.
        * **macOS:** Terminal.
        * **Linux:** Any terminal application.

    ## 2. Running the Container

    1.  **Open your Terminal or Command Prompt.**
    2.  **Choose a Version:** You can run the `latest` version or a specific version tag if available (e.g., `1.2.4`). Check Docker Hub ([https://hub.docker.com/r/buckeye90/vsm-generator-app/tags](https://hub.docker.com/r/buckeye90/vsm-generator-app/tags) - *assuming this is your repo*) for available tags.
    3.  **Run the application:** Copy and paste the appropriate command into your terminal and press Enter:

        * **To run the `latest` version:**
            ```bash
            docker run -d -p 8080:8080 --name vsm-generator-container buckeye90/vsm-generator-app:latest
            ```
            *(You can often omit `:latest` as it's the default)*

        * **To run a specific version (e.g., `1.2.4`):**
            ```bash
            docker run -d -p 8080:8080 --name vsm-generator-container-1.2.4 buckeye90/vsm-generator-app:1.2.4
            ```
            *(Note: Using a different container name like `--name vsm-generator-container-1.2.4` is recommended if you might run multiple versions)*

    4.  **Wait for Docker:** Docker will first check if the specified image tag exists locally. If not, it will download ("pull") it from Docker Hub. Once downloaded, it will start the container. This might take a moment the first time.

    *What the command does:*
    * `docker run`: Starts a new container.
    * `-d`: Runs the container in the background.
    * `-p 8080:8080`: Connects port 8080 on your computer to port 8080 inside the container. You can change the first `8080` if that port is busy on your machine (e.g., `-p 8081:8080`).
    * `--name vsm-generator-container...`: Gives the container a memorable name.
    * `buckeye90/vsm-generator-app:TAG`: The name and specific tag of the Docker image to use.

    ## 3. Accessing the Web Interface

    1.  Once the container is running, open your web browser.
    2.  Navigate to the address: `http://localhost:8080` (or the host port you specified, e.g., `http://localhost:8081`).
    3.  You should see the "Value Stream Map Mermaid Generator" web page. Check the footer for the specific version built into the image.

    ## 4. Using the Interface

    1.  **(Optional) Diagram Title:** Enter a title for your diagram.
    2.  **Fill in the Steps:** Enter names, process times, and wait times for each step using the form. Use "Add Another Step" as needed.
    3.  **Generate Code:** Click "**Generate Mermaid Code**".
    4.  **Get the Output:** Review the code. Use "**Copy Code**" or "**Save as Markdown (.md)**".

    ## 5. Stopping and Removing the Container

    When finished, stop and optionally remove the container using the name you assigned.

    1.  **Open your Terminal or Command Prompt.**
    2.  **Stop the container:**
        ```bash
        # Example for the 'latest' container name
        docker stop vsm-generator-container

        # Example for a specific version container name
        docker stop vsm-generator-container-1.2.4
        ```
    3.  **(Optional) Remove the container:**
        ```bash
        # Example for the 'latest' container name
        docker rm vsm-generator-container

        # Example for a specific version container name
        docker rm vsm-generator-container-1.2.4
        ```

    ## 6. Troubleshooting

    * **Cannot access `http://localhost:8080`:** Check Docker is running, the container is running (`docker ps`), and the port mapping is correct.
    * **`docker run` command fails:** Check the image name and tag exist on Docker Hub or locally. Check for typos. Ensure Docker is running and you are logged in if it's a private repository.
    ```
