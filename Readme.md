# File Processor Script

## Description
A Python script that processes files with a specified extension in a given directory. For each matching file, it:
1. Creates a new output path in a dedicated `test` directory
2. Executes a custom system command with the original and new file paths
3. Supports dry runs and verbose output

## Usage
```bash
python main.py <source_directory> <file_extension> <command_prefix> [options]
```

## Arguments
| Argument | Description |
|---------|-------------|
| `source_directory` | Directory to search for files |
| `file_extension` | File extension (e.g., `txt`, `jpg`) |
| `command_prefix` | System command with optional arguments (e.g., `cp`, `magick -resize 50%`) |
| `--dry-run` | Simulate execution without running commands |
| `--verbose` | Show detailed command output |

## Example
```bash
python main.py /path/to/files txt cp --dry-run
```
This would:
- Find all `.txt` files in `/path/to/files`
- Copy them to `/path/to/test/` with `test_` prefix
- Show progress in the terminal without executing commands

## Notes
- Output files are saved in a `test` directory relative to the source
- New filenames start with `test_` followed by the original name
- For commands with `%` (e.g., ImageMagick), use `%%` in the command prefix
- Requires the specified command to be installed in your PATH

## License
MIT License (see LICENSE file for details)
