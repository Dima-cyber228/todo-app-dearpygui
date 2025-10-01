import dearpygui.dearpygui as dpg
from src.ui.menu_bar import create_menu_bar

# --- Тема ---
def apply_theme():
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

def main():
    dpg.create_context()
    dpg.create_viewport(title="ToDo App", width=1200, height=800)

    apply_theme()

    with dpg.window(label="ToDo App", no_title_bar=True, no_resize=True, no_move=True, pos=(0,0), width=1200, height=800):
        with dpg.group(horizontal=True):
            create_menu_bar()

            # Правая панель (пока пустая)
            with dpg.child_window(width=-1, border=False):
                dpg.add_text("Main Content Area", color=(200, 200, 200))

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main() 
