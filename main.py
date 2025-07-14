import os
import sys
import subprocess
import argparse
import math # For math.ceil
import glob


# ANSI escape codes for colors
COLOR_GREEN = "\033[92m"   # Success
COLOR_YELLOW = "\033[93m"  # Information/Warning
COLOR_RED = "\033[91m"    # Error
COLOR_BLUE = "\033[94m"   # Paths/Secondary info
COLOR_CYAN = "\033[96m"   # General info
COLOR_RESET = "\033[0m"   # Reset to default color

_TOTAL_FILES_TO_PROCESS = 0
_PROCESSED_FILES_COUNT = 0

# Function to print progress bar
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50, color_bar=COLOR_GREEN, color_text=COLOR_YELLOW):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
        color_bar   - Optional  : ANSI color code for the filled part of the bar
        color_text  - Optional  : ANSI color code for the text parts
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(bar_length * iteration // total)
    bar = color_bar + '█' * filled_length + COLOR_RESET + '-' * (bar_length - filled_length)
    # The \r makes it overwrite the current line
    sys.stdout.write(f'\r{color_text}{prefix} |{bar}| {percent}% {suffix}{COLOR_RESET}')
    sys.stdout.flush() # Ensure it's printed immediately

def get_new_filepath(source_dir, original_file_path,original_name,output_file_prefix,output_base_dir):

    # Recalculate paths for the current file
    relative_path = os.path.relpath(original_file_path, source_dir)
    new_file_name = f"{output_file_prefix}{original_name}"
    relative_output_dir = os.path.join(output_base_dir, os.path.dirname(relative_path))

    os.makedirs(relative_output_dir, exist_ok=True)
    return os.path.join(relative_output_dir, new_file_name)
   

def get_files_and_dirs(base_dir, pattern=""):
    """
    Returns a list of tuples [(filename, filedir), ...] for all files matching the given pattern in base_dir and subdirectories.

    Parameters:
        base_dir (str): The root directory to search from.
        pattern (str): A glob-style file name pattern to match. Use `**/*` for recursive searches.
    """
    full_pattern = os.path.join(base_dir, "**", pattern)
    result = []
    
    # Search all files matching the pattern in subdirectories
    for file_path in glob.glob(full_pattern, recursive=True):
        filename = os.path.basename(file_path)
        result.append((filename, file_path))
    
    return result

def process_file( original_file_path, new_file_path, command_prefix, dry_run=False,verbose=False):
    global _PROCESSED_FILES_COUNT , _TOTAL_FILES_TO_PROCESS
    # Detailed logs for the current file (these print on new lines and will scroll)
    print(f"\n{COLOR_YELLOW}Processing ({_PROCESSED_FILES_COUNT}/{_TOTAL_FILES_TO_PROCESS}):{COLOR_RESET} {COLOR_BLUE}{original_file_path}{COLOR_RESET}")
    print(f"  {COLOR_YELLOW}Output to:{COLOR_RESET} { COLOR_BLUE}{new_file_path}{ COLOR_RESET}")
   
    system_command =  command_prefix + [ original_file_path, new_file_path]
    print(f"  {COLOR_YELLOW}Command:{COLOR_RESET} {COLOR_CYAN}{' '.join(system_command)}{ COLOR_RESET}")

    print_progress(_PROCESSED_FILES_COUNT - 1, _TOTAL_FILES_TO_PROCESS, 
                   prefix='Progress:',
                   suffix=f'({_PROCESSED_FILES_COUNT}/{_TOTAL_FILES_TO_PROCESS} files)', bar_length=40)
    if dry_run:
        print(f"  {COLOR_BLUE}(Dry run: Command not executed){ COLOR_RESET}")
    else:
        try:
            
            result = subprocess.run(system_command, check=True, capture_output=True, text=True)
            
            # Clear the line where the progress bar was, before printing success/error
            print("\r" + " " * 200 + "\r", end="")
            print(f"{COLOR_GREEN}✔ Success.{ COLOR_RESET}")

            if verbose:
                if result.stdout:
                    print(f"  {COLOR_CYAN}  STDOUT: {result.stdout.strip()}{ COLOR_RESET}")
                if result.stderr:
                    print(f"  {COLOR_CYAN}  STDERR: {result.stderr.strip()}{ COLOR_RESET}")
        except KeyboardInterrupt:
            print("\r" + " " * 200 + "\r", end=" ")
            # Clear line even on error
            print(f"  {COLOR_RED}✖ Closing script... { COLOR_RESET}")
            exit(0)
        
        except FileNotFoundError:
            print("\r" + " " * 200 + "\r", end=" ") # Clear line even on error
            print(f"  {COLOR_RED}✖ Error: Command '{system_command[0]}' not found. Make sure it's in your PATH.{ COLOR_RESET}")
        except subprocess.CalledProcessError as e:
            print("\r" + " " * 200 + "\r", end=" ") # Clear line even on error
            print(f"  {COLOR_RED}✖ Error executing command (exit code {e.returncode}):{ COLOR_RESET}")
            print(f"  {COLOR_RED}  Command: {' '.join(e.cmd)}{ COLOR_RESET}")
            if e.stdout:
                print(f"  {COLOR_RED}  STDOUT: {e.stdout.strip()}{ COLOR_RESET}")
            if e.stderr:
                print(f"  {COLOR_RED}  STDERR: {e.stderr.strip()}{ COLOR_RESET}")
        except Exception as e:
            print("\r" + " " * 200 + "\r", end=" ") # Clear line even on error
            print(f"  {COLOR_RED}✖ An unexpected error occurred: {e}{ COLOR_RESET}")
        
def process_files(source_dir, pattern, command_prefix, dry_run=False, verbose=False, output_file_prefix="new_", output_base_dir="processed_files"):
    """
    Finds files with a specific extension in a source directory,
    creates new destination paths, and executes a system command.

    Args:
        source_dir (str): The root directory to search for files.
        pattern (str): A glob-style file name pattern to match. Use `**/*` for recursive searches.
    """
    global _PROCESSED_FILES_COUNT , _TOTAL_FILES_TO_PROCESS
    if not os.path.isdir(source_dir):
        print(f"{COLOR_RED}Error: Source directory '{source_dir}' not found or is not a directory.{ COLOR_RESET}")
        sys.exit(1)

    os.makedirs(output_base_dir, exist_ok=True)
    print(f"{COLOR_CYAN}Created/Ensured output base directory: {output_base_dir}{ COLOR_RESET}")
    
    print(f"{COLOR_CYAN}Scanning for files...{ COLOR_RESET}")
    files_to_process = get_files_and_dirs(source_dir,pattern)
    _TOTAL_FILES_TO_PROCESS = len(files_to_process)
    

    if _TOTAL_FILES_TO_PROCESS == 0:
        print(f"{COLOR_YELLOW}No files with pattern '{pattern}' found in '{source_dir}'. Exiting.{ COLOR_RESET}")
        sys.exit(0) # Exit gracefully if no files found

    print(f"{COLOR_CYAN}Found {_TOTAL_FILES_TO_PROCESS} file(s) to process.{ COLOR_RESET}")
    # --- End of Step 1 ---
    _PROCESSED_FILES_COUNT = 1 
    print(f"{COLOR_YELLOW}\n--- Starting File Processing ---{ COLOR_RESET}")
    
    for (filename, full_filepath) in files_to_process:
        new_file_path = get_new_filepath(source_dir , full_filepath, filename, output_file_prefix, output_base_dir )
        print(full_filepath)
        process_file( full_filepath, new_file_path, command_prefix,dry_run=dry_run, verbose=verbose)
        _PROCESSED_FILES_COUNT += 1
                     
    # Final update of the progress bar to ensure it's 品 and then a newline
    print_progress(_TOTAL_FILES_TO_PROCESS, _TOTAL_FILES_TO_PROCESS, prefix='Progress:', suffix=f'({_TOTAL_FILES_TO_PROCESS}/{_TOTAL_FILES_TO_PROCESS} files)', bar_length=40)
    sys.stdout.write('\n') # Move to the next line after the progress bar is complete

    print(f"{COLOR_YELLOW}\n--- Processing Complete ---{ COLOR_RESET}")
    print(f"{COLOR_GREEN}Summary: Found {_TOTAL_FILES_TO_PROCESS} files, successfully processed {_TOTAL_FILES_TO_PROCESS}.{ COLOR_RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process files with a specific extension, create new paths, and execute a custom system command.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "source_directory",
        help="The path to the directory containing files to be processed. The script will recursively search this directory."
    )
    parser.add_argument(
        "command_prefix",
        nargs=argparse.REMAINDER,
        help="The system command to execute for each file, followed by its initial arguments.\n"
             "The script will append the original file path and the new destination path.\n"
             "Example for copying: `cp`\n"
             "Example for ImageMagick: `magick -resize 50%% -quality 80`\n"
             "Note: For commands with '%%' in their arguments, use '%%' to escape them if running from shell."
    )
    parser.add_argument(
        "--file_pattern" ,"-pt",
        default="*",
        help="The file extension to filter by (e.g., 'txt', 'jpg', 'pdf'). Do not include the leading dot."
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Perform a 'dry run'. Commands will be printed but NOT executed. Useful for testing."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output. Shows STDOUT/STDERR of commands even on success."
    )
    parser.add_argument(
        "--output-file-prefix",
        "-ofp",
        default="p_", # Default to no prefix
        help="Optional prefix to add to the new file name (e.g., 'processed_')."
    )
    parser.add_argument(
        "--output-basedir",
        "-osd",
        default="processed",
        help="Optional subdirectory path (e.g., 'subfolder/another') to insert into the output structure.\n"
             "Example: 'YOUR_SUBDIR/original/relative/path/new_file.ext'."
    )

    args = parser.parse_args()

    if not args.command_prefix:
        parser.error("You must provide a system command to execute (e.g., `cp`, `magick`).\n"
                     "Refer to --help for examples.")

    print(f"{COLOR_CYAN}Starting script with arguments:{ COLOR_RESET}")
    print(f"{COLOR_CYAN}Source Directory:{ COLOR_RESET} {args.source_directory}")
    print(f"{COLOR_CYAN}File pattern:{ COLOR_RESET} .{args.file_pattern}")
    print(f"{COLOR_CYAN}Command Prefix:{ COLOR_RESET} {args.command_prefix}")
    print(f"{COLOR_CYAN}Dry Run:{ COLOR_RESET} {args.dry_run}")
    print(f"{COLOR_CYAN}Verbose Mode:{ COLOR_RESET} {args.verbose}")
    print(f"{COLOR_CYAN}Output File Prefix:{ COLOR_RESET} '{args.output_file_prefix}'")
    print(f"{COLOR_CYAN}Output Subdirectory:{ COLOR_RESET} '{args.output_basedir}'")
    print(f"{COLOR_CYAN}{'-' * 40}{ COLOR_RESET}")

    process_files(
        source_dir=args.source_directory,
        pattern=args.file_pattern,
        command_prefix=args.command_prefix,
        dry_run=args.dry_run,
        verbose= args.verbose,
        output_file_prefix=args.output_file_prefix,
        output_base_dir=args.output_basedir,
    )
