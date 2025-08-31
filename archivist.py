#!/usr/bin/env python
import os
import argparse
import sys
from pathlib import Path
from internetarchive import get_item, exceptions

def get_user_input(metadata_keys):
    """Prompt the user for required and optional metadata."""
    print("📚 Please provide the metadata for your Archive.org item.")
    metadata = {}
    for key, prompt, required in metadata_keys:
        while True:
            value = input(f"{prompt}: ").strip()
            if value or not required:
                if value:
                    metadata[key] = value
                break
            print(f"❌ This field is required.")
    return metadata

def upload_folder(identifier, metadata, target_folder, non_interactive=False):
    """
    Uploads all files from a target folder to a specified Internet Archive item.
    """
    print("\n🚀 Starting upload process...")
    print(f"→ Target Identifier: {identifier}")

    try:
        # Get the item object, which represents the collection on Archive.org
        item = get_item(identifier)

        # Find all files in the target folder, excluding this script
        script_name = Path(__file__).name
        files_to_upload = [
            str(p) for p in Path(target_folder).rglob('*')
            if p.is_file() and p.name != script_name
        ]

        if not files_to_upload:
            print("No files found to upload (excluding the script itself).")
            return

        print(f"Found {len(files_to_upload)} file(s) to potentially upload.")

        # Confirm before proceeding in interactive mode
        if not non_interactive:
            confirm = input("Do you want to proceed with the upload? (y/n): ").lower()
            if confirm != 'y':
                print("Upload cancelled by user.")
                return

        # --- MODIFICATION START ---
        # This new block replaces the incompatible 'remote_path_prefix' argument.
        # It manually creates a mapping of where files should go on the server
        # to preserve the directory structure.

        print("Building file list for upload...")
        files_for_upload_dict = {}
        base_folder_path = Path(target_folder)

        for local_file_path_str in files_to_upload:
            local_path = Path(local_file_path_str)
            # This calculates the path as it should appear on archive.org
            remote_path = local_path.relative_to(base_folder_path)
            # The key is the remote path, the value is the local source file
            files_for_upload_dict[str(remote_path)] = local_file_path_str

        print(f"Uploading {len(files_for_upload_dict)} files with their directory structure...")

        # The upload function handles skipping existing files, retries, and progress bars.
        # It's verbose by default, showing progress.
        item.upload(
            files_for_upload_dict, # We now pass our specially constructed dictionary
            metadata=metadata,
            verbose=True
        )
        # --- MODIFICATION END ---


        print(f"\n✅ Upload process complete.")
        print(f"View your item at: https://archive.org/details/{identifier}")

    except exceptions.AuthenticationError:
        print("\n❌ Authentication Error: Could not connect to Archive.org.")
        print("Please run 'ia configure' in your terminal to set up your credentials.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

def main():
    """Main function to parse arguments and start the uploader."""
    parser = argparse.ArgumentParser(
        description="""📚 Archivist Pro: A robust tool to upload a folder's contents
                       to the Internet Archive.""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'folder',
        nargs='?',
        default='.',
        help='The local folder to upload. Defaults to the current directory.'
    )
    parser.add_argument('-i', '--identifier', help='The unique identifier for the Archive.org item.')
    parser.add_argument('-t', '--title', help='The title of the item.')
    parser.add_argument('-c', '--creator', help='The creator or author of the item.')
    parser.add_argument('-m', '--mediatype', help='The media type (e.g., "texts", "movies", "data").')
    parser.add_argument('--description', help='A description for the item.')
    parser.add_argument('--subjects', help='Comma-separated subjects or tags.')
    parser.add_argument('--year', help='The publication year of the item.')
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Skip all interactive prompts and proceed with upload.'
    )

    args = parser.parse_args()

    target_folder = os.path.abspath(args.folder)
    if not os.path.isdir(target_folder):
        print(f"❌ Error: Folder not found at '{target_folder}'")
        sys.exit(1)

    print(f"📁 Preparing to upload contents of: {target_folder}")

    metadata_prompts = [
        # (key, prompt, required)
        ('identifier', 'Enter a unique identifier', True),
        ('title', 'Enter a title', True),
        ('creator', 'Enter the creator/author', True),
        ('mediatype', 'Enter media type (e.g., texts, movies, data)', True),
        ('description', 'Enter a description (optional)', False),
        ('subject', 'Enter subjects/tags, comma-separated (optional)', False),
        ('date', 'Enter year (optional)', False),
    ]

    # Populate metadata from arguments or prompt the user
    metadata = {}
    cli_metadata_provided = False

    # Check if essential metadata is provided via command line
    if args.identifier and args.title and args.creator and args.mediatype:
        cli_metadata_provided = True
        metadata['identifier'] = args.identifier
        metadata['title'] = args.title
        metadata['creator'] = args.creator
        metadata['mediatype'] = args.mediatype
        if args.description: metadata['description'] = args.description
        if args.subjects: metadata['subject'] = args.subjects
        if args.year: metadata['date'] = args.year
    elif args.yes:
        print("❌ Error: Cannot run in non-interactive mode (-y) without providing all required metadata via arguments.")
        print("Required: --identifier, --title, --creator, --mediatype")
        sys.exit(1)

    if not cli_metadata_provided:
        # Filter prompts for what's missing
        missing_prompts = [p for p in metadata_prompts if getattr(args, p[0], None) is None]
        user_metadata = get_user_input(missing_prompts)

        # Combine CLI args and user input
        for key, _, _ in metadata_prompts:
             if getattr(args, key, None):
                 # map 'subjects' to 'subject' and 'year' to 'date' for metadata dict
                 meta_key = 'subject' if key == 'subjects' else ('date' if key == 'year' else key)
                 metadata[meta_key] = getattr(args, key)
        metadata.update(user_metadata)

    # The identifier is special and not part of the standard metadata dict for the upload function
    identifier = metadata.pop('identifier')

    upload_folder(identifier, metadata, target_folder, non_interactive=args.yes)

if __name__ == "__main__":
    main()