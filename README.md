# Bookmarks HTML Generator

Generates a responsive HTML page from your bookmarks (currently, only Firefox is supported). The script fetches bookmarks from your profile, formats them into a readable HTML layout, and includes incremental search.

## Features

- Fetches bookmarks from your (Firefox) profile.
- Displays bookmarks in a responsive HTML page, in a panel per folder.
- Separate sections for Bookmarks Toolbar and Bookmarks Menu
- Includes a search bar for incremental searching.
- Outputs the HTML file with a masonry layout for folder organization.

## Prerequisites

- Python 3.7 or higher

## 1. Install Required Python Packages

Before running the script, you'll need to install the required Python packages. You can install them using `pip`.

1. **Install the Required Packages**

   Navigate to the project directory and run the following command:

   ```
   pip install -r requirements.txt
   ```

   This command installs all the necessary packages listed in the `requirements.txt` file.

## 2. Usage

1. **Clone the Repository**

   ```
   git clone https://github.com/edoloughlin/bookmarks2html.git
   cd bookmarks2html
   ```

2. **Run the Script**

   The main script is `make-page.py`. To run it, use the following command:

   ```
   python3 make-page.py
   ```

   This will generate an HTML file named `firefox_bookmarks.html` in your home directory.

3. **View the Generated HTML**

   Open the generated `bookmarks.html` file in your web browser to view your bookmarks.

## Customization

- You can modify the `template.html` file to customize the appearance of the generated HTML page.
- The CSS styles within `template.html` can be adjusted to change the layout, colors, and fonts.

## Troubleshooting

- If the script can't find your Firefox profile, verify the profile path and adjust the script if necessary.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
