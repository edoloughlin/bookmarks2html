# Firefox Bookmarks HTML Generator

This project generates responsive HTML pages from your Firefox bookmarks. The scripts fetch bookmarks from your Firefox profile, format them into a readable HTML layout, and include incremental search functionality.

## Features

- Fetches bookmarks from your Firefox profile.
- Displays bookmarks in a responsive HTML page.
- Provides separate sections for the Bookmarks Toolbar and Bookmarks Menu.
- Includes a search bar for incremental searching.
- Outputs HTML files with a masonry layout for folder organization.
- Allows grouping bookmarks by the date they were added or last updated.
- Supports full folder hierarchy display and customizable date formats.

## Project Structure

The project follows a conventional Python project structure:

```
/your-project-directory/
│
├── /bookmark_utils/       # A package for common utilities
│   ├── __init__.py        # Makes bookmark_utils a package
│   ├── utils.py           # Contains the functions extracted from scripts
│
├── /templates/            # Directory for HTML templates
│   ├── template.html
│   ├── grouped-template.html
│
├── /static/               # Directory for static files like CSS, JS, etc.
│   ├── css/
│   │   ├── common.css     # CSS file used in HTML templates
│
├── /scripts/              # Directory for Python scripts
│   ├── make_page.py       # Script to generate standard bookmarks HTML
│   ├── grouped_bookmarks.py  # Script to generate grouped bookmarks HTML
│
├── /output/               # Directory for generated HTML output files
│   └── (HTML files)       # HTML files will be saved here
│
├── README.md              # Documentation about the project
├── requirements.txt       # List of dependencies, if any
└── .gitignore             # Git ignore file to exclude unnecessary files
```

## Prerequisites

- Python 3.7 or higher

## Installation

1. **Clone the Repository**

   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Required Packages**

   If there are any dependencies, you can install them using the following command:

   ```
   pip install -r requirements.txt
   ```

## Usage

### Generate Standard Bookmarks HTML

1. Navigate to the `scripts/` directory:

   ```
   cd scripts
   ```

2. Run the `make_page.py` script:

   ```
   python3 make_page.py
   ```

3. The generated HTML file (`firefox_bookmarks.html`) will be saved in the `output/` directory.

### Generate Grouped Bookmarks HTML

1. Navigate to the `scripts/` directory:

   ```
   cd scripts
   ```

2. Run the `grouped_bookmarks.py` script:

   ```
   python3 grouped_bookmarks.py
   ```

3. The generated HTML file (`grouped_firefox_bookmarks.html`) will be saved in the `output/` directory.

## Customization

- You can modify the HTML templates located in the `templates/` directory to change the appearance of the generated HTML pages.
- CSS styles can be adjusted in the `static/css/common.css` file.

## Troubleshooting

- If the script cannot find your Firefox profile, ensure that Firefox is installed and that the profile path is correct.
- Ensure Firefox is closed when running the script to avoid database locking issues.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
