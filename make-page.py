import sqlite3
import os
import platform
import shutil
import tempfile
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def get_firefox_profile_path():
    os_name = platform.system()
    if os_name == "Linux":
        snap_base_path = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/")
        if os.path.exists(snap_base_path):
            base_path = snap_base_path
        else:
            base_path = os.path.expanduser("~/.mozilla/firefox/")
    elif os_name == "Darwin":  # macOS
        base_path = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
    elif os_name == "Windows":
        base_path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles\\")
    else:
        raise Exception("Unsupported operating system")

    for profile in os.listdir(base_path):
        profile_path = os.path.join(base_path, profile)
        if os.path.isdir(profile_path) and "places.sqlite" in os.listdir(profile_path):
            return os.path.join(profile_path, "places.sqlite")

    raise FileNotFoundError("places.sqlite not found in any Firefox profile")

def fetch_tags(cursor):
    cursor.execute("""
        SELECT t.id, t.title, p.url 
        FROM moz_bookmarks AS t
        JOIN moz_bookmarks AS bt ON t.id = bt.parent
        JOIN moz_places AS p ON bt.fk = p.id
        WHERE t.parent = (SELECT id FROM moz_bookmarks WHERE title = 'Tags' AND type = 2)
    """)
    tag_data = cursor.fetchall()
    
    tags = {}
    for tag_id, tag_title, url in tag_data:
        if url not in tags:
            tags[url] = []
        tags[url].append(tag_title)
    return tags

def fetch_bookmarks(db_path):
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "places.sqlite")

    try:
        shutil.copy2(db_path, temp_db_path)
        conn = sqlite3.connect(f"file:{temp_db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        tags = fetch_tags(cursor)

        ROOT_FOLDERS = {
            'toolbar': 3,  # Bookmarks Toolbar
            'menu': 2  # Bookmarks Menu
        }

        bookmarks_data = {}

        for section, root_id in ROOT_FOLDERS.items():
            section_data = []
            fetch_top_level_bookmarks(cursor, root_id, section_data, tags)
            fetch_folders(cursor, root_id, "", section_data, tags)
            bookmarks_data[section] = section_data

        conn.close()
        return bookmarks_data

    finally:
        shutil.rmtree(temp_dir)

def fetch_top_level_bookmarks(cursor, parent_id, section_data, tags):
    cursor.execute("""
        SELECT b.id, b.title, p.url, k.keyword
        FROM moz_bookmarks b
        LEFT JOIN moz_places p ON b.fk = p.id
        LEFT JOIN moz_keywords k ON b.keyword_id = k.id
        WHERE b.parent = ?
        AND b.type = 1
        ORDER BY b.dateAdded DESC
    """, (parent_id,))
    bookmarks = cursor.fetchall()

    if bookmarks:
        section_data.append({
            'folder_title': "Top Level",
            'bookmarks': [{'title': b[1] or b[2], 'url': b[2], 'tags': ', '.join(tags.get(b[2], [])), 'keyword': b[3]} for b in bookmarks]
        })

def fetch_folders(cursor, parent_id, parent_path, section_data, tags):
    cursor.execute("""
        SELECT id, title
        FROM moz_bookmarks
        WHERE parent = ?
        AND type = 2
        ORDER BY title
    """, (parent_id,))
    folders = cursor.fetchall()

    for folder_id, folder_title in folders:
        full_path = parent_path + ("/" if parent_path else "") + (folder_title or "Unnamed Folder")

        cursor.execute("""
            SELECT b.id, b.title, p.url, k.keyword
            FROM moz_bookmarks b
            LEFT JOIN moz_places p ON b.fk = p.id
            LEFT JOIN moz_keywords k ON b.keyword_id = k.id
            WHERE b.parent = ?
            AND b.type = 1
            ORDER BY b.dateAdded DESC
        """, (folder_id,))
        bookmarks = cursor.fetchall()

        if bookmarks:
            section_data.append({
                'folder_title': full_path,
                'bookmarks': [{'title': b[1] or b[2], 'url': b[2], 'tags': ', '.join(tags.get(b[2], [])), 'keyword': b[3]} for b in bookmarks]
            })

        # Recursively fetch child folders
        fetch_folders(cursor, folder_id, full_path, section_data, tags)

def generate_html(bookmarks_data, output_path):
    env = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template('template.html')
    rendered_html = template.render(
        bookmarks_data=bookmarks_data,
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"Bookmarks HTML generated at: {output_path}")

if __name__ == "__main__":
    try:
        db_path = get_firefox_profile_path()
        output_file = os.path.expanduser("~/firefox_bookmarks.html")
        bookmarks = fetch_bookmarks(db_path)
        generate_html(bookmarks, output_file)
    except Exception as e:
        print(f"Error: {e}")
