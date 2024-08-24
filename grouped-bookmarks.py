from bookmark_utils import get_firefox_profile_path, generate_html, build_full_folder_path
import sqlite3
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
        one_month_ago = today - timedelta(days=30)
        start_of_year = today.replace(month=1, day=1)
        start_of_last_year = start_of_year.replace(year=start_of_year.year - 1)
        
        categories = {
            "Today": [],
            "This Week": [],
            "This Month": [],
            "This Year": [],
            "Last Year": [],
            "Older": []
        }

        cursor.execute("""
            SELECT b.title, p.url, datetime(b.dateAdded/1000000, 'unixepoch') as date_added, 
                   datetime(b.lastModified/1000000, 'unixepoch') as last_modified,
                   b.parent
            FROM moz_bookmarks b
            LEFT JOIN moz_places p ON b.fk = p.id
            WHERE p.url IS NOT NULL
            ORDER BY b.dateAdded DESC
        """)
        bookmarks = cursor.fetchall()

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
            elif bookmark_time >= start_of_last_year:
                categories["Last Year"].append(bookmark_info)
            else:
                categories["Older"].append(bookmark_info)

        conn.close()
        return categories

    finally:
        shutil.rmtree(temp_dir)

def format_category_title(category_name, today, one_week_ago, start_of_year):
    if category_name == "Today":
        return f"Today ({today.strftime('%Y-%m-%d')})"
    elif category_name == "This Week":
        return f"This Week ({one_week_ago.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')})"
    elif category_name == "This Month":
        return f"This Month ({today.strftime('%B')})"
    elif category_name == "This Year":
        return f"This Year ({today.strftime('%Y')})"
    elif category_name == "Last Year":
        return f"Last Year ({today.year - 1})"
    else:
        return f"Older ({start_of_year.year - 1} and earlier)"

if __name__ == "__main__":
    try:
        db_path = get_firefox_profile_path()
        bookmarks_by_date = fetch_bookmarks_grouped_by_date(db_path)
        today = datetime.now()
        one_week_ago = today - timedelta(weeks=1)
        start_of_year = today.replace(month=1, day=1)

        context = {
            'bookmarks_by_date': bookmarks_by_date,
            'category_titles': {category: format_category_title(category, today, one_week_ago, start_of_year)
                                for category in bookmarks_by_date.keys()},
            'generated_date': today.isoformat()
        }
        generate_html('grouped-template.html', context, 'grouped_firefox_bookmarks.html')
    except Exception as e:
        print(f"Error: {e}")
