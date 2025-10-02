import dearpygui.dearpygui as dpg
from ..utils.storage import get_tasks, get_task_by_id, update_task as update_task_in_db
from ..utils.consts import CATEGORIES

def update_menu_bar():
    # Удаляем старое меню
    dpg.delete_item("menu_container", children_only=True)

    with dpg.group(parent="menu_container"):
        for cat in CATEGORIES:  # используем CATEGORIES из consts
            dpg.add_button(
                label=cat,
                width=-1,
                callback=on_category_click,
                user_data=cat
            )

# --- Обработчик выбора категории ---
def on_category_click(sender, app_data, user_data):
    category = user_data
    print(f"Выбрана категория: {category}")
    dpg.set_value("section_header", category)  # обновляем заголовок
    update_task_list(category)

def update_task_list(section="Сегодня", parent_id=None):
    print(f"[DEBUG] Обновление задач для секции: {section}, parent_id: {parent_id}")
    # Удаляем старые задачи
    dpg.delete_item("tasks_container", children_only=True)

    tasks = get_tasks(section=section, parent_id=parent_id)
    print(f"[DEBUG] Найдено задач: {len(tasks)}")

    if not tasks:
        dpg.add_text("Нет задач", parent="tasks_container")
        return

    with dpg.group(parent="tasks_container"):
        for task in tasks:
            print(f"[DEBUG] Задача: {task.title} (ID: {task.id}, Completed: {task.completed})")
            with dpg.group(horizontal=True, parent="tasks_container"):
                checkbox = dpg.add_checkbox(
                    default_value=task.completed,
                    callback=lambda s, d, u: toggle_task(u),
                    user_data=task.id
                )
                dpg.add_spacer(width=5)

                # Время (если есть)
                if task.due_date:
                    dpg.add_text(task.due_date, color=(100, 180, 255))

                dpg.add_spacer(width=5)

                # Название задачи
                dpg.add_text(task.title)

                dpg.add_spacer(width=5)

                # Описание (если есть)
                if task.description:
                    dpg.add_text(f"({task.description})", color=(200, 200, 200))

                dpg.add_spacer(width=5)

                # Категория
                category_color = get_category_color(task.category)
                dpg.add_text(f"● {task.category}", color=category_color)

                dpg.add_spacer(width=5)

                # Кнопка "Добавить подзадачу"
                dpg.add_button(
                    label="Добавить подзадачу",
                    small=True,
                    callback=lambda s, d, u: open_add_subtask_modal(u),
                    user_data=task.id
                )

                dpg.add_spacer(width=5)

                # Кнопка "Редактировать"
                dpg.add_button(
                    label="Редактировать",
                    small=True,
                    callback=lambda s, d, u: open_edit_task_modal(u),
                    user_data=task.id
                )

            # Прогресс-бар (если есть подзадачи)
            progress = calculate_task_progress(task.id)
            if progress < 100:
                dpg.add_progress_bar(
                    default_value=progress / 100,  # от 0 до 1
                    width=-1,
                    overlay=f"{progress}%"
                )
                dpg.add_spacer(height=5)

            # Показываем подзадачи, если они есть
            subtasks = get_tasks(parent_id=task.id)
            if subtasks:
                print(f"[DEBUG] Подзадачи для {task.title}: {len(subtasks)}")
                with dpg.tree_node(label="Подзадачи", parent="tasks_container"):
                    for subtask in subtasks:
                        with dpg.group(horizontal=True, parent="tasks_container"):
                            dpg.add_checkbox(
                                default_value=subtask.completed,
                                callback=lambda s, d, u: toggle_task(u),
                                user_data=subtask.id
                            )
                            dpg.add_spacer(width=5)

                            # Название подзадачи
                            dpg.add_text(subtask.title)

                            dpg.add_spacer(width=5)

                            # Описание подзадачи (если есть)
                            if subtask.description:
                                dpg.add_text(f"({subtask.description})", color=(200, 200, 200))

                            dpg.add_spacer(width=5)

                            # Категория подзадачи
                            category_color = get_category_color(subtask.category)
                            dpg.add_text(f"● {subtask.category}", color=category_color)

                            dpg.add_spacer(width=5)

                            # Кнопка "Редактировать подзадачу"
                            dpg.add_button(
                                label="Редактировать",
                                small=True,
                                callback=lambda s, d, u: open_edit_task_modal(u),
                                user_data=subtask.id
                            )

# --- Открытие модального окна для подзадачи ---
def open_add_subtask_modal(parent_task_id):
    import datetime
    dpg.set_value("add_subtask_parent_id", str(parent_task_id))  # ✅ правильный тег
    current_section = dpg.get_value("section_header")
    dpg.set_value("add_task_section_input", current_section)  # ✅ правильный тег

    # Установим сегодняшнюю дату
    today = datetime.date.today()
    dpg.set_value("add_task_date_picker", {
        "year": today.year,
        "month": today.month - 1,
        "day": today.day
    })

    dpg.show_item("add_task_modal")

def calculate_task_progress(task_id):
    from ..utils.storage import get_tasks

    subtasks = get_tasks(parent_id=task_id)
    if not subtasks:
        return 100  # если нет подзадач, то 100%

    total = len(subtasks)
    completed = sum(1 for subtask in subtasks if subtask.completed)
    progress = (completed / total) * 100 if total > 0 else 0
    return round(progress, 2)

# --- Открытие модального окна для редактирования задачи ---
def open_edit_task_modal(task_id):
    import datetime
    from ..utils.storage import get_task_by_id

    task = get_task_by_id(task_id)

    # Заполняем поля
    dpg.set_value("edit_task_title_input", task.title)
    dpg.set_value("edit_task_description_input", task.description)

    # Устанавливаем дату
    if task.due_date:
        date_parts = task.due_date.split("-")
        year = int(date_parts[0])
        month = int(date_parts[1]) - 1  # Dear PyGui использует 0-based месяцы
        day = int(date_parts[2])
        dpg.set_value("edit_task_date_picker", {"year": year, "month": month, "day": day})
    else:
        today = datetime.date.today()
        dpg.set_value("edit_task_date_picker", {"year": today.year, "month": today.month - 1, "day": today.day})

    # Устанавливаем секцию (категорию)
    dpg.set_value("edit_task_section_input", task.section)

    # Устанавливаем parent_id (если это подзадача)
    if task.parent_id:
        dpg.set_value("edit_subtask_parent_id", str(task.parent_id))
    else:
        dpg.set_value("edit_subtask_parent_id", "")

    # Запоминаем ID задачи для обновления
    dpg.set_value("edit_task_id_input", str(task.id))

    dpg.show_item("edit_task_modal")

def toggle_task(task_id):
    from ..utils.storage import get_task_by_id, update_task as update_task_in_db

    task = get_task_by_id(task_id)
    task.completed = not task.completed
    task.section = "Завершенные" if task.completed else task.section  # перемещаем в "Завершенные", если выполнена
    update_task_in_db(task)

    # Обновляем текущую секцию
    current_section = dpg.get_value("section_header")
    update_task_list(current_section)

def get_category_color(category_name):
    colors = {
        "Работа": (100, 200, 255),
        "Образование": (255, 200, 100),
        "Здоровье": (255, 100, 100),
        "Машина": (150, 150, 255),
        "Дом": (200, 255, 100),
        "Тренировки": (255, 150, 200),
        "Подарки": (255, 255, 100),
        "Идеи": (200, 200, 255),
        "Книги": (150, 255, 255),
        "Семья": (255, 100, 255),
        "Путешествия": (100, 255, 100),
    }
    return colors.get(category_name, (200, 200, 200))

def create_menu_bar():
    with dpg.child_window(width=200, border=False):
        dpg.add_text("Входящие", color=(200, 200, 200))
        dpg.add_spacer(height=10)
        with dpg.child_window(width=-1, height=-1, tag="menu_container", border=False):
            update_menu_bar()