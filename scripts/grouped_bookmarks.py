from bookmark_utils.utils import get_firefox_profile_path, generate_html, build_full_folder_path
import os
import shutil
import sqlite3
import tempfile  # Import tempfile to handle temporary files
from datetime import datetime, timedelta

def fetch_bookmarks_grouped_by_date(db_path):
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "places.sqlite")

    try:
        shutil.copy2(db_path, temp_db_path)
        conn = sqlite3.connect(f"file:{temp_db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        today = datetime.now()
        one_day_ago = today - timedelta(days=1)
        one_week_ago = today - timedelta(weeks=1)
        one_month_ago = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        categories = {
            "Today": [],
            "This Week": [],
            "This Month": [],
            "This Year": []
        }

        cursor.execute("""
            SELECT b.title, p.url, datetime(b.dateAdded/1000000, 'unixepoch') as date_added, 
                   datetime(b.lastModified/1000000, 'unixepoch') as last_modified,
                   b.parent
            FROM moz_bookmarks b
            LEFT JOIN moz_places p ON b.fk = p.id
            WHERE p.url IS NOT NULL
            ORDER BY date_added DESC
        """)
        bookmarks = cursor.fetchall()

        yearly_categories = {}

        for title, url, date_added, last_modified, parent_id in bookmarks:
            folder_path = build_full_folder_path(cursor, parent_id)
            bookmark_time = datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S')

            bookmark_info = {
                "title": title,
                "url": url,
                "date_added": date_added,
                "last_modified": last_modified,
                "folder": folder_path
            }

            if bookmark_time >= one_day_ago:
                categories["Today"].append(bookmark_info)
            elif bookmark_time >= one_week_ago:
                categories["This Week"].append(bookmark_info)
            elif bookmark_time >= one_month_ago:
                categories["This Month"].append(bookmark_info)
            elif bookmark_time >= start_of_year:
                categories["This Year"].append(bookmark_info)
            else:
                year = bookmark_time.year
                if year not in yearly_categories:
                    yearly_categories[year] = []
                yearly_categories[year].append(bookmark_info)

        # Merge categories and sort the yearly categories in descending order
        sorted_categories = {**categories, **{year: yearly_categories[year] for year in sorted(yearly_categories, reverse=True)}}

        conn.close()
        return sorted_categories

    finally:
        shutil.rmtree(temp_dir)

def format_category_title(category_name):
    """Format the category title for predefined and yearly categories."""
    return str(category_name) if isinstance(category_name, int) else category_name

if __name__ == "__main__":
    try:
        db_path = get_firefox_profile_path()
        bookmarks_by_date = fetch_bookmarks_grouped_by_date(db_path)

        context = {
            'bookmarks_by_date': bookmarks_by_date,
            'category_titles': {key: format_category_title(key) for key in bookmarks_by_date.keys()},
            'generated_date': datetime.now().isoformat()
        }
        generate_html('grouped-template.html', context, 'grouped_firefox_bookmarks.html')
    except Exception as e:
        print(f"Error: {e}")
