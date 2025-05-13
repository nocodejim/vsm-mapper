    # Instructions: Running the VSM Generator UI Test

    This guide explains how to set up and run the automated UI test script (`test_vsm_generator.py`) for the Value Stream Map Mermaid Generator. The script uses Python and Selenium to interact with the web interface running in its Docker container.

    ## 1. Prerequisites

    1.  **Python 3 & pip:** Ensure Python 3 and pip are installed.
    2.  **Docker:** Docker Desktop (or Docker Engine) must be installed and **running**.
    3.  **Google Chrome:** Must be installed.
    4.  **ChromeDriver:** Handled via `webdriver-manager` (installed below).
    5.  **Running VSM Container:** The VSM generator container must be running. You can start it using `scripts/deploy.sh [VERSION]` (which now handles building with version tags) or the `docker run` command for a pre-built image tag (e.g., `buckeye90/vsm-generator-app:1.2.4`). Ensure it's accessible at `http://localhost:8080`.

    ## 2. Setup Steps

    1.  **Save the Test Script:** Place `test_vsm_generator.py` in a `tests` directory (e.g., `vsm_mermaid_generator/tests/test_vsm_generator.py`).
    2.  **Navigate to Project Root:** Open terminal, `cd` to the project root (`vsm_mermaid_generator`).
    3.  **Use Setup Script (Recommended):** Run the test environment setup script:
        ```bash
        ./scripts/setup_test_env.sh
        ```
        This creates the `.venv` directory and installs dependencies using the correct virtual environment pip.
    4.  **Activate Virtual Environment:** Activate the `.venv` environment **every time** you open a new terminal for testing:
        * macOS/Linux: `source .venv/bin/activate`
        * Windows CMD: `.\.venv\Scripts\activate.bat`
        * Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
        *(Your prompt should change, e.g., `(.venv) your-prompt$`)*
    5.  **(If not using setup script) Create & Activate Venv Manually:**
        * Create: `python3 -m venv .venv`
        * Activate (see commands above).
        * Install Dependencies (inside venv): `pip install selenium webdriver-manager`
    6.  **Configure Download Directory in Script:**
        * **CRITICAL:** Edit `tests/test_vsm_generator.py` and set the `DOWNLOAD_DIR` variable to an appropriate absolute path for your system.
        * Save the script.
    7.  **(If not using setup script) Add to `.gitignore`:** Ensure `.venv/` is in your `.gitignore` file.

    ## 3. Running the Test

    1.  **Start the VSM Container:** Ensure the correct version is running via `scripts/deploy.sh [VERSION]` or `docker run ...`.
    2.  **Open Terminal & Navigate:** Open terminal, `cd` to project root.
    3.  **Activate Virtual Environment:** `source .venv/bin/activate` (or equivalent).
    4.  **Execute the Script:**
        ```bash
        python tests/test_vsm_generator.py
        ```

    ## 4. Interpreting the Output

    * Look for status messages and the final ✅ or ❌ result.
    * Review errors listed if the test fails.

    ## 5. Deactivating the Environment

    * When done, type: `deactivate`

    ## 6. Troubleshooting

    * **`ModuleNotFoundError`:** Activate the venv (`source .venv/bin/activate`) before running `python`. Ensure dependencies were installed using `setup_test_env.sh` or `pip install` inside the venv.
    * **`WebDriverException` / ChromeDriver issues:** Ensure `webdriver-manager` installed correctly via setup script or pip. Check Chrome compatibility if issues persist.
    * **Element Not Found / Timeout:** Ensure container is running & responsive. Check test script selectors against `app/index.html`. The version displayed in the footer might change - the test currently doesn't check the footer, but be aware if adding checks later.
    * **Download Issues:** Check `DOWNLOAD_DIR` path and permissions in `test_vsm_generator.py`.
    * **Content Mismatch:** Examine the difference printed. Adjust `EXPECTED_MERMAID_OUTPUT` in the test script or fix the generator code.
    ```
