# Archivist : Internet Archive Folder Uploader

`Archivist` is a robust Python command-line tool designed to simplify the process of uploading a complete folder structure to a new or existing item on the Internet Archive (archive.org).

It handles recursive file searching, metadata input, and preserves your original directory layout on the server, making it ideal for backing up projects, datasets, or collections in a single command.

## Key Features

*   **Recursive Upload:** Automatically finds and uploads all files within a directory and all its subdirectories.
*   **Preserves Directory Structure:** Recreates your local folder hierarchy perfectly on the Internet Archive item.
*   **Flexible Metadata:** Provide all required metadata via command-line arguments for automation, or use the interactive prompts to be guided through the process.
*   **Non-Interactive Mode:** A `-y` flag allows the script to run without any user confirmation, perfect for use in automated workflows and shell scripts.
*   **Smart and Safe:** The script is safe to re-run. The underlying `internetarchive` library will automatically skip any files that have already been successfully uploaded.

## Requirements

*   Python 3.x
*   The `internetarchive` Python library.

## Installation & Setup

1.  **Install the library:**
    ```bash
    pip install internetarchive
    ```

2.  **Configure your Internet Archive account:** You only need to do this once. The tool will securely save your credentials for all future uploads.
    ```bash
    ia configure
    ```

## Usage

The script can be run in two primary ways:

#### 1. Interactive Mode (Recommended for first-time use)

Navigate to the folder you want to upload and run the script. It will prompt you for all the necessary information.

```bash
# Go into the directory you want to upload
cd /path/to/my_project

# Run the script
python /path/to/archivist.py
```

The script will then ask for the unique identifier, title, creator, etc.

#### 2. Non-Interactive Mode (For automation)

Provide all the required metadata as command-line arguments. This is perfect for scripting. The first argument is the folder to upload (or `.` for the current directory).

**Example:**
```bash
python archivist.py /path/to/my_project \
    -i "my-project-archive-2025-08" \
    -t "My Project Archive (August 2025)" \
    -c "Your Name" \
    -m "data" \
    --description "A complete backup of the My Project folder." \
    --subjects "backup, project files, dataset" \
    --year "2025" \
    -y
```
