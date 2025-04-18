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

