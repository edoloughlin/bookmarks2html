import os
import platform
import sqlite3
import shutil
import tempfile
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

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

def build_full_folder_path(cursor, folder_id):
    cursor.execute("SELECT title, parent FROM moz_bookmarks WHERE id = ?", (folder_id,))
    folder = cursor.fetchone()
    if folder and folder[1] > 1:
        parent_path = build_full_folder_path(cursor, folder[1])
        return f"{parent_path}/{folder[0]}" if parent_path else folder[0]
    return folder[0] if folder else ''

def read_common_css():
    with open("common.css", "r", encoding="utf-8") as f:
        return f.read()

def generate_html(template_name, context, output_filename):
    env = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template(template_name)

    common_css = read_common_css()
    context['common_css'] = common_css
    rendered_html = template.render(context)

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"HTML file generated at: {output_path}")
