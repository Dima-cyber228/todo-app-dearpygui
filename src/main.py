import dearpygui.dearpygui as dpg
from src.ui.menu_bar import create_menu_bar, update_task_list
from src.utils.storage import init_db

def main():
    init_db()
    print("Database initialized")

    dpg.create_context()
    print("Context created")

    # --- Шрифты ---
    with dpg.font_registry():
        with dpg.font("C:/Windows/Fonts/segoeui.ttf", 18) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    dpg.bind_font(default_font)
    print("Font bound")

    dpg.create_viewport(title="ToDo App", width=1200, height=800)
    print("Viewport created")

    # --- Тема ---
    with dpg.theme() as dark_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 20))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (240, 240, 240))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 30, 40))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 60))
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (100, 200, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (20, 20, 30))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)

    dpg.bind_theme(dark_theme)

    with dpg.window(label="ToDo App", no_title_bar=True, no_resize=True, no_move=True, pos=(0,0), width=1200, height=800):
        with dpg.group(horizontal=True):
            create_menu_bar()

            # --- Правая панель ---
            with dpg.child_window(width=-1, border=False):
                header = dpg.add_text("Сегодня", tag="section_header")  # кириллица!
                dpg.add_spacer(height=10)

                # Кнопка добавления задачи
                dpg.add_button(label="Добавить задачу", callback=lambda: open_add_task_modal())

                # Контейнер для задач
                with dpg.child_window(height=-25, border=False, tag="tasks_container"):
                    update_task_list("Сегодня")  # кириллица

    # --- Модальное окно добавления задачи ---
    with dpg.window(label="Добавить задачу", modal=True, show=False, tag="add_task_modal", no_title_bar=False, width=400):
        dpg.add_input_text(label="Заголовок", tag="add_task_title_input")
        
        # Убираем выбор категории
        # dpg.add_combo(...)
        # dpg.add_input_text(...)

        dpg.add_input_text(label="Описание", tag="add_task_description_input", multiline=True, height=50)
        
        # Календарь
        dpg.add_text("Дата выполнения", tag="date_label")
        dpg.add_date_picker(tag="add_task_date_picker", level=dpg.mvDatePickerLevel_Day)

        dpg.add_input_text(tag="add_subtask_parent_id", show=False, default_value="")
        dpg.add_input_text(tag="add_task_section_input", show=False, default_value="Сегодня")
        dpg.add_button(label="Сохранить", callback=lambda: save_task())

    # --- Модальное окно редактирования задачи ---
    with dpg.window(label="Редактировать задачу", modal=True, show=False, tag="edit_task_modal", no_title_bar=False, width=400):
        dpg.add_input_text(label="Заголовок", tag="edit_task_title_input")
        dpg.add_input_text(label="Описание", tag="edit_task_description_input", multiline=True, height=50)
        
        # Календарь
        dpg.add_text("Дата выполнения", tag="edit_date_label")
        dpg.add_date_picker(tag="edit_task_date_picker", level=dpg.mvDatePickerLevel_Day)

        dpg.add_input_text(tag="edit_subtask_parent_id", show=False, default_value="")
        dpg.add_input_text(tag="edit_task_section_input", show=False, default_value="Сегодня")
        dpg.add_input_text(tag="edit_task_id_input", show=False, default_value="")  # ID задачи
        dpg.add_button(label="Сохранить", callback=lambda: update_task_from_modal())

    print("Before start_dearpygui")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    print("After start_dearpygui")
    dpg.destroy_context()

def update_task_from_modal():
    from src.models.task import Task
    from src.utils.storage import get_task_by_id, update_task as update_task_in_db
    import datetime

    task_id = int(dpg.get_value("edit_task_id_input"))
    task = get_task_by_id(task_id)

    # Обновляем поля
    task.title = dpg.get_value("edit_task_title_input")
    task.description = dpg.get_value("edit_task_description_input")

    # Обновляем дату
    date_obj = dpg.get_value("edit_task_date_picker")
    if date_obj is not None and 'day' in date_obj:
        task.due_date = f"{date_obj['year']}-{date_obj['month']+1:02d}-{date_obj['day']:02d}"
    else:
        today = datetime.date.today()
        task.due_date = f"{today.year}-{today.month:02d}-{today.day:02d}"

    task.section = dpg.get_value("edit_task_section_input")

    # Обновляем в БД
    update_task_in_db(task)

    # Закрываем модальное окно
    dpg.hide_item("edit_task_modal")

    # Очищаем поля
    dpg.set_value("edit_task_title_input", "")
    dpg.set_value("edit_task_description_input", "")
    dpg.set_value("edit_subtask_parent_id", "")
    dpg.set_value("edit_task_section_input", "Сегодня")
    dpg.set_value("edit_task_id_input", "")

    # Установим сегодняшнюю дату в календаре (для следующего открытия)
    today = datetime.date.today()
    dpg.set_value("edit_task_date_picker", {
        "year": today.year,
        "month": today.month - 1,
        "day": today.day
    })

    # Обновляем список задач
    current_section = dpg.get_value("section_header")
    print(f"[DEBUG] Обновление списка задач для секции: {current_section}")
    from src.ui.menu_bar import update_task_list
    update_task_list(current_section)

def open_add_task_modal():
    import datetime
    today = datetime.date.today()
    dpg.set_value("add_task_date_picker", {
        "year": today.year,
        "month": today.month - 1,
        "day": today.day
    })
    current_section = dpg.get_value("section_header")
    dpg.set_value("add_task_section_input", current_section)
    dpg.show_item("add_task_modal")

def save_task():
    from src.models.task import Task
    from src.utils.storage import add_task
    import datetime

    title = dpg.get_value("add_task_title_input")
    
    # Берём текущую секцию как категорию
    current_section = dpg.get_value("section_header")
    category = current_section

    description = dpg.get_value("add_task_description_input")
    parent_id_str = dpg.get_value("add_subtask_parent_id")
    section = current_section  # сохраняем задачу в текущей секции

    # Получаем выбранную дату из календаря
    date_obj = dpg.get_value("add_task_date_picker")
    if date_obj is not None and 'day' in date_obj:
        due_date = f"{date_obj['year']}-{date_obj['month']+1:02d}-{date_obj['day']:02d}"
    else:
        today = datetime.date.today()
        due_date = f"{today.year}-{today.month:02d}-{today.day:02d}"

    print(f"[DEBUG] Сохранение задачи: '{title}', категория: '{category}', дата: {due_date}, описание: '{description}', parent_id: {parent_id_str}, section: {section}")

    parent_id = int(parent_id_str) if parent_id_str and parent_id_str != "" else None

    new_task = Task(
        id=None,
        title=title,
        category=category,
        due_date=due_date,
        description=description,
        section=section,
        parent_id=parent_id
    )
    task_id = add_task(new_task)
    print(f"[DEBUG] Задача сохранена с ID: {task_id}, section: {section}")

    # --- Добавляем новую категорию в меню ---
    from src.utils.consts import CATEGORIES
    from src.ui.menu_bar import update_menu_bar
    if category not in CATEGORIES:
        CATEGORIES.append(category)
        update_menu_bar()  # обновляем меню

    # Закрываем модальное окно
    dpg.hide_item("add_task_modal")
    # Очищаем поля
    dpg.set_value("add_task_title_input", "")
    dpg.set_value("add_task_description_input", "")
    dpg.set_value("add_subtask_parent_id", "")
    dpg.set_value("add_task_section_input", "Сегодня")

    # Установим сегодняшнюю дату в календаре (для следующего открытия)
    today = datetime.date.today()
    dpg.set_value("add_task_date_picker", {
        "year": today.year,
        "month": today.month - 1,
        "day": today.day
    })

    # Обновляем список задач
    current_section = dpg.get_value("section_header")
    print(f"[DEBUG] Обновление списка задач для секции: {current_section}")
    update_task_list(current_section)

if __name__ == "__main__":
    main()