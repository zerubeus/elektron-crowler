# Elektron Crawler

A Python tool that crawls Elektronauts forum threads and converts them into readable PDF documents. This tool is particularly useful for archiving or offline reading of forum content.

## Features

- Fetches complete forum threads from Elektronauts
- Processes HTML content while preserving formatting
- Converts emoji images to text
- Removes unsupported elements (like audio)
- Generates clean, well-formatted PDF documents
- Handles large threads by fetching posts in batches
- Command-line interface for easy thread selection

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/elektron-crowler.git
cd elektron-crowler
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the thread ID as an argument. The thread ID can be found in the Elektronauts forum URL (e.g., for `https://www.elektronauts.com/t/222373`, the thread ID is "222373"):

```bash
python src/app.py 222373
```

The script will generate a PDF file named `thread_content_[THREAD_ID].pdf` in the current directory.

For help with command-line options:

```bash
python src/app.py --help
```

## Output

The generated PDF includes:

- Sequential post numbering
- Original post content
- Preserved text formatting
- Emoji conversions
- Clean layout and spacing

## Project Structure

```
elektron-crowler/
├── src/
│   └── app.py         # Main application code
├── requirements.txt   # Project dependencies
└── README.md         # This file
```

## Dependencies

- `requests`: For making HTTP requests to the forum
- `beautifulsoup4`: For HTML parsing
- `reportlab`: For PDF generation

## License

MIT License

## Contributing

Feel free to open issues or submit pull requests with improvements.

```

```
