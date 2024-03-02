import pyautogui

class GestureCommands:
    @staticmethod
    def double_click(button="left"):
        pyautogui.click(clicks=2, button=button)

    @staticmethod
    def right_click():
        pyautogui.rightClick()

    @staticmethod
    def scroll_up(lines=20):
        pyautogui.scroll(lines)

    @staticmethod
    def scroll_down(lines=20):
        pyautogui.scroll(-lines)

    @staticmethod
    def cut_text():
        pyautogui.hotkey("ctrl", "x")

    @staticmethod
    def copy_text():
        pyautogui.hotkey("ctrl", "c")

    @staticmethod
    def paste_text():
        pyautogui.hotkey("ctrl", "v")

    @staticmethod
    def minimize_window():
        pyautogui.hotkey("winleft", "m")

    @staticmethod
    def maximize_window():
        pyautogui.hotkey("winleft", "up")

    @staticmethod
    def do_go_back():
        pyautogui.hotkey("alt", "left")

    @staticmethod
    def do_go_forward():
        pyautogui.hotkey("alt", "right")

    @staticmethod
    def do_undo():
        pyautogui.hotkey("ctrl", "z")

    @staticmethod
    def do_redo():
        pyautogui.hotkey("ctrl", "y")


gesture_commands_instance = GestureCommands()

gesture_mapping = {
    "Double Click": gesture_commands_instance.double_click,
    "Right Click": gesture_commands_instance.right_click,
    "Scroll Up": gesture_commands_instance.scroll_up,
    "Scroll Down": gesture_commands_instance.scroll_down,
    "Cut Text": gesture_commands_instance.cut_text,
    "Copy Text": gesture_commands_instance.copy_text,
    "Paste Text": gesture_commands_instance.paste_text,
    "Minimize Window": gesture_commands_instance.minimize_window,
    "Maximize Window": gesture_commands_instance.maximize_window,
    "Go Back": gesture_commands_instance.do_go_back,
    "Go Forward": gesture_commands_instance.do_go_forward,
    "Undo": gesture_commands_instance.do_undo,
    "Redo": gesture_commands_instance.do_redo,
}