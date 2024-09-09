from bookmark_utils.utils import get_firefox_profile_path, generate_html, build_full_folder_path
import shutil
import sqlite3
import tempfile
import os
from datetime import datetime

def fetch_bookmarks(db_path):
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "places.sqlite")

    try:
        shutil.copy2(db_path, temp_db_path)
        conn = sqlite3.connect(f"file:{temp_db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        ROOT_FOLDERS = {
            'toolbar': 3,  # Bookmarks Toolbar
            'menu': 2  # Bookmarks Menu
        }

        bookmarks_data = {}

        for section, root_id in ROOT_FOLDERS.items():
            section_data = []
            fetch_top_level_bookmarks(cursor, root_id, section_data)
            fetch_folders(cursor, root_id, "", section_data)
            bookmarks_data[section] = section_data

        conn.close()
        return bookmarks_data

    finally:
        shutil.rmtree(temp_dir)

def fetch_top_level_bookmarks(cursor, parent_id, section_data):
    cursor.execute("""
        SELECT b.id, b.title, p.url, k.keyword, 
               (SELECT GROUP_CONCAT(a.content, ', ') 
                FROM moz_items_annos a 
                JOIN moz_anno_attributes n ON n.id = a.anno_attribute_id 
                WHERE a.item_id = b.id AND n.name = 'bookmarkProperties/placesUI')
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
            'bookmarks': [{'title': b[1] or b[2], 'url': b[2], 'tags': b[4], 'keyword': b[3]} for b in bookmarks]
        })

def fetch_folders(cursor, parent_id, parent_path, section_data):
    cursor.execute("""
        SELECT id, title
        FROM moz_bookmarks
        WHERE parent = ?
        AND type = 2
        ORDER BY title
    """, (parent_id,))
    folders = cursor.fetchall()

    for folder_id, folder_title in folders:
        full_path = build_full_folder_path(cursor, folder_id)

        cursor.execute("""
            SELECT b.id, b.title, p.url, k.keyword, 
                   (SELECT GROUP_CONCAT(a.content, ', ') 
                    FROM moz_items_annos a 
                    JOIN moz_anno_attributes n ON n.id = a.anno_attribute_id 
                    WHERE a.item_id = b.id AND n.name = 'bookmarkProperties/placesUI')
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
                'bookmarks': [{'title': b[1] or b[2], 'url': b[2], 'tags': b[4], 'keyword': b[3]} for b in bookmarks]
            })

        fetch_folders(cursor, folder_id, full_path, section_data)

if __name__ == "__main__":
    try:
        db_path = get_firefox_profile_path()
        bookmarks = fetch_bookmarks(db_path)
        generated_date = datetime.now().isoformat()  # ISO 8601 timestamp

        context = {
            'bookmarks_data': bookmarks,
            'generated_date': generated_date
        }
        generate_html('template.html', context, 'firefox_bookmarks.html')
    except Exception as e:
        print(f"Error: {e}")
