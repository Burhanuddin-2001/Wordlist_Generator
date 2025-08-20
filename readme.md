# Wordlist Generator

## Description

This project is a high-performance Python script designed to generate wordlists by creating combinations from a given set of base words. It leverages multiprocessing to significantly speed up the generation process, making it an efficient tool for learning and experimentation.

This script is intended strictly for educational purposes within the field of cybersecurity, such as understanding password complexity, the mechanics of dictionary attacks, and the importance of strong password policies.

## Features

-   **Parallel Processing**: Utilizes Python's `multiprocessing` module to leverage multiple CPU cores for rapid generation.
-   **Efficient I/O**: Implements a producer-consumer model with a dedicated writer process to prevent I/O bottlenecks and ensure smooth performance.
-   **Targeted Generation**: Allows users to generate combinations that result in a specific final password length.
-   **Safety Cap**: Includes a built-in feasibility limit (1 billion combinations) to prevent accidental generation of excessively large files in non-targeted mode.
-   **User-Friendly CLI**: Simple and clear command-line interface for easy operation.
-   **Progress Tracking**: A `tqdm` progress bar provides real-time feedback on the generation process.

## Installation / Setup

1.  **Clone the repository:**
    ```
    git clone https://github.com/Burhanuddin-2001/Wordlist_Generator.git
    cd Wordlist_Generator
    ```

2.  **Install dependencies:**
    The script requires the `tqdm` library. You can install it using pip.
    ```
    pip install tqdm
    ```

3.  **Prepare your word file:**
    Create a text file (e.g., `words.txt`) containing the base words you want to combine, with one word per line.

## Usage

The script is run from the command line and accepts several arguments to customize the wordlist generation.

### Basic Usage

To generate a wordlist from a file named `words.txt` and save it to the default `wordlist.txt`:

```
python generator.py --file words.txt
```

### Specifying an Output File

To specify a custom name for the output file:

```
python generator.py --file words.txt --output my_custom_list.txt
```

### Targeting a Specific Length

To generate only combinations that result in a password of exactly 12 characters:

```
python generator.py --file words.txt --output passwords_12_char.txt --length 12
```

### Adjusting Processes

To run the script using a specific number of CPU processes (e.g., 4):

```
python generator.py --file words.txt --processes 4
```

*Note: If `--processes` is not specified, the script defaults to using all available CPU cores on your system.*

### Command-Line Arguments

| Argument          | Short | Description                                                               | Required | Default                               |
| ----------------- | ----- | ------------------------------------------------------------------------- | :------: | ------------------------------------- |
| `--file`          | `-f`  | Path to the file containing base words.                                   |   Yes    | N/A                                   |
| `--output`        | `-o`  | Name of the file to save the wordlist to.                                 |    No    | `wordlist.txt`                        |
| `--length`        | `-l`  | Generate only passwords of this exact length.                             |    No    | Disabled                              |
| `--processes`     | `-p`  | Number of processes to use.                                               |    No    | System's CPU core count               |

---

## Disclaimer

-   This project is provided for **educational and non-commercial use only**.
-   The author is **not responsible** for any misuse or damage caused by this script. Users are responsible for their own actions and must comply with all applicable laws.
-   Selling or distributing this script/software for profit is strictly **prohibited**. Legal action may be taken against any individuals or entities who violate this condition.

## License

This project is licensed under the terms specified in the [LICENSE.TXT](LICENSE.txt) file located in this repository.
