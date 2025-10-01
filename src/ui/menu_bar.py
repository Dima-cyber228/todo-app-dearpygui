 
import dearpygui.dearpygui as dpg

# --- Категории ---
CATEGORIES = [
    ("Today", "star"),
    ("Upcoming", "calendar"),
    ("Calendar", "calendar"),
    ("Favorites", "heart"),
    ("Work", "briefcase"),
    ("Health", "heart"),
    ("Housekeeping", "home"),
    ("Car", "car"),
    ("Education", "book"),
    ("Workout", "dumbbell"),
    ("Gifts", "gift"),
    ("Ideas", "lightbulb"),
    ("Books", "book-open"),
]

# --- Обработчик выбора категории ---
def on_category_click(sender, app_data, user_data):
    category = user_data
    print(f"Выбрана категория: {category}")
    # Здесь будет вызов функции обновления задач

def create_menu_bar():
    with dpg.child_window(width=200, border=False):
        dpg.add_text("Inbox", color=(200, 200, 200))
        dpg.add_spacer(height=10)
        for cat, icon in CATEGORIES:
            dpg.add_button(
                label=f"{icon} {cat}",
                width=-1,
                callback=on_category_click,
                user_data=cat
            )