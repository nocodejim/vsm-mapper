# Value Stream Map (VSM) Mermaid Generator

This project provides a simple web interface to generate Mermaid syntax for Value Stream Maps. It allows users to define VSM steps with process and wait times, and then generates the corresponding Mermaid code. Additionally, it supports importing existing Mermaid VSM code to populate the editor.

## Features

* **Dynamic Step Creation:** Easily add, insert, and remove steps in your Value Stream Map.
* **Time Inputs:** Specify process time for each step and wait time between steps.
* **Automatic Metrics Calculation:** Calculates Total Process Time, Total Wait Time, Lead Time, and Flow Efficiency.
* **Mermaid Code Generation:** Outputs `graph LR` Mermaid syntax, including a subgraph for the calculated VSM metrics.
* **Import Existing Diagrams:** Load VSM data by pasting existing Markdown (containing a Mermaid block) or raw Mermaid code directly into the tool.
* **Code Output & Export:**
    * Display generated Mermaid code in a read-only text area.
    * "Copy Code" button to easily copy the syntax.
    * "Save as Markdown (.md)" button to download a complete Markdown file with a title and the Mermaid code block.
* **Dockerized Application:** Easy to deploy and run using Docker.
* **Version Display:** Footer shows application and image build versions (when deployed via the provided `deploy.sh` script with versioning).

## Project Structure

* `/app`: Contains the web interface (`index.html`) and its `Dockerfile`.
* `/diagrams`: The recommended directory to save your user-generated `.mmd` or `.md` files.
* `/scripts`: Contains helper scripts:
    * `init_project.sh`: Sets up the basic project structure.
    * `deploy.sh`: Builds the Docker image and runs the web application container.
    * `setup_test_env.sh`: Sets up the Python virtual environment for automated UI testing.
* `/tests`: Contains automated UI tests (`test_vsm_generator.py`) and test instructions.
* `README.md`: This file.
* `instructions.md`: Comprehensive guide for setting up the entire project from scratch.
* `container_only_usage.md`: Guide for users who only want to run a pre-built Docker image.

## Quick Start

1.  **Prerequisites:** Ensure Docker is installed and running.
2.  **Clone/Download Project:** Get the project files onto your local machine.
3.  **Build and Deploy:**
    * Navigate to the project's root directory in your terminal.
    * Run the deployment script: `./scripts/deploy.sh` (you can optionally pass a version tag like `./scripts/deploy.sh 1.0.0`).
4.  **Access the Application:** Open your web browser and go to `http://localhost:8080`.

## Using the VSM Generator

### Creating a New Diagram

1.  **Diagram Title (Optional):** Enter a title for your VSM. This will be used in the downloaded Markdown file.
2.  **Define Steps:**
    * The interface starts with one step.
    * **Step Name:** Enter a descriptive name for the step (e.g., "Requirement Gathering").
    * **Process Time:** Enter the time taken to complete this step (e.g., "2 days", "4h").
    * **Wait Time:** For all steps *except the first*, enter the waiting time that occurs *before* this step begins (e.g., "1 day", "2h"). Leave blank for the first step.
    * **Add Step at End:** Click this button to append a new step to the end of your VSM.
    * **Add Step Before (Plus Icon):** Click the `+` icon next to a step's "Remove" button to insert a new step *before* that specific step.
    * **Remove Step (X Icon):** Click the `X` icon to remove a specific step. The first step cannot be removed if it's the only one.
3.  **Generate Code:** Once all steps are defined, click the "**Generate Mermaid Code**" button.
4.  **Review Output:**
    * The generated Mermaid syntax will appear in the "Generated Mermaid Code" text area.
    * Calculated metrics (Total Process Time, Lead Time, Flow Efficiency) will be included as a subgraph.
5.  **Use the Code:**
    * Click "**Copy Code**" to copy the syntax to your clipboard.
    * Click "**Save as Markdown (.md)**" to download a Markdown file containing the diagram title and the Mermaid code block.

### Loading an Existing Diagram from Text

You can also load an existing VSM diagram if you have its Mermaid code or a Markdown file containing it.

1.  **Locate the Import Section:** Scroll down below the "Generated Mermaid Code" output area. You will find a button labeled "**Load Diagram from Text**".
2.  **Expand the Section:** Click the "**Load Diagram from Text**" button. This will expand a section allowing you to input your code. The button text will change to "Hide Diagram Import".
3.  **Paste Your Code:** In the "Paste Markdown or Mermaid Code" textarea, paste either:
    * The raw Mermaid code for your VSM (starting with `graph LR` or similar).
    * The full content of a Markdown file that includes a Mermaid code block (e.g., ```mermaid ... ```). The tool will attempt to extract the Mermaid part.
4.  **Parse and Load:** Click the "**Parse and Load**" button.
    * The tool will attempt to parse the VSM steps from your pasted text.
    * If successful, the "Create or Modify Diagram Steps" form above will be cleared and repopulated with the steps from your imported diagram.
    * You will see a success or error message below the "Parse and Load" button.
5.  **Clear Import Text (Optional):** If you want to clear the pasted text from the import textarea, click the "**Clear Text**" button.
6.  **Modify and Generate:** Once loaded, you can modify the steps in the form as if you created them manually, and then click "**Generate Mermaid Code**" to get updated Mermaid syntax or save a new Markdown file.
7.  **Collapse the Section:** Click "**Hide Diagram Import**" to collapse the import section.

## Viewing Generated Diagrams

Mermaid code can be rendered by various tools:

* Online editors like the official [Mermaid Live Editor](https://mermaid.live).
* Markdown editors and previewers with Mermaid support (e.g., VS Code with Mermaid extensions, Obsidian, Typora).
* Documentation generators like MkDocs (with plugins), Docusaurus, etc.

## Stopping the Application

To stop the Docker container running the application:

1.  Find the container ID or name (default is `vsm-generator-container` if deployed with `deploy.sh`): `docker ps`
2.  Stop the container: `docker stop <container_id_or_name>`
3.  Optionally, remove the container: `docker rm <container_id_or_name>`

## Further Information

* For detailed setup from scratch (including script creation): `instructions.md`
* For running a pre-built Docker image: `container_only_usage.md`
* For setting up and running UI tests: `tests/test_instructions.md`
