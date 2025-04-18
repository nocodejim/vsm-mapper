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
    2.  **Run the application:** Copy and paste the following command into your terminal and press Enter:

        ```bash
        docker run -d -p 8080:8080 --name vsm-generator-container buckeye90/vsm-generator-app
        ```

    3.  **Wait for Docker:** Docker will first check if the image `buckeye90/vsm-generator-app` exists locally. If not, it will download ("pull") it from Docker Hub. Once downloaded, it will start the container. This might take a moment the first time.

    *What the command does:*
    * `docker run`: Starts a new container.
    * `-d`: Runs the container in the background.
    * `-p 8080:8080`: Connects port 8080 on your computer to port 8080 inside the container, allowing you to access the web interface.
    * `--name vsm-generator-container`: Gives the container a memorable name.
    * `buckeye90/vsm-generator-app`: The name of the Docker image to use.

    ## 3. Accessing the Web Interface

    1.  Once the container is running (the `docker run` command finishes without errors), open your web browser (like Chrome, Firefox, Edge, Safari).
    2.  Navigate to the following address: `http://localhost:8080`
    3.  You should see the "Value Stream Map Mermaid Generator" web page.

    *Note:* If port `8080` was already in use on your computer, you might have changed the command (e.g., to `-p 8081:8080`). In that case, you would access the interface at `http://localhost:8081`.

    ## 4. Using the Interface

    1.  **(Optional) Diagram Title:** Enter a title for your diagram. This will be used if you save the output as a Markdown file.
    2.  **Fill in the Steps:**
        * For the first step, enter its name (e.g., "Feature Request") and its **Process Time** (e.g., "2 days"). Leave **Wait Time** blank.
        * Click "**Add Another Step**" to add subsequent steps.
        * For all steps after the first, enter the step name, its **Process Time**, and the **Wait Time** *before* this step begins (e.g., "5 days"). Wait Time is required for all steps except the first.
        * Use the "Remove" button next to a step (if available) to delete it.
    3.  **Generate Code:** When all steps are entered, click "**Generate Mermaid Code**".
    4.  **Get the Output:**
        * The generated Mermaid code will appear in the text box at the bottom.
        * Click "**Copy Code**" to copy it to your clipboard. You can then paste this into any tool that supports Mermaid (like VS Code with a Mermaid extension, online editors like mermaid.live, etc.).
        * Alternatively, click "**Save as Markdown (.md)**" to download a complete Markdown file containing your diagram title and the Mermaid code block. This file will be saved to your browser's default download location.

    ## 5. Stopping and Removing the Container

    When you are finished using the application, you can stop and optionally remove the container to free up resources.

    1.  **Open your Terminal or Command Prompt.**
    2.  **Stop the container:**
        ```bash
        docker stop vsm-generator-container
        ```
    3.  **(Optional) Remove the container:** If you don't plan to use it again soon and want to clean up, remove the stopped container:
        ```bash
        docker rm vsm-generator-container
        ```
        *(You can always recreate it later by running the `docker run` command again.)*

    ## 6. Troubleshooting

    * **Cannot access `http://localhost:8080`:**
        * Make sure Docker Desktop (or Docker Engine) is running.
        * Verify the container is running using the command `docker ps`. You should see `vsm-generator-container` or the image name `buckeye90/vsm-generator-app` in the list.
        * Check if another application on your computer is already using port 8080. If so, stop the other application, or stop and remove the container (`docker stop/rm vsm-generator-container`) and restart it using a different host port (e.g., `docker run -d -p 8081:8080 ...` then access `http://localhost:8081`).
    * **`docker run` command fails:** Read the error message carefully. It might indicate Docker isn't running, there was a typo in the image name, or there are network issues preventing the image download.
    ```
