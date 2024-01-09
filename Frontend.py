import tkinter as tk
from threading import Thread

import Virtual_Mouse


class HandTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Tracking App")

        self.start_button = tk.Button(root, text="Start", command=self.start_hand_tracking)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_hand_tracking)
        self.stop_button.pack(pady=10)

        self.virtual_mouse = Virtual_Mouse.VirtualMouse(self)

        self.is_tracking = False

    def start_hand_tracking(self):
        if not self.is_tracking:
            self.is_tracking = True
            Thread(target=self.virtual_mouse.hand_tracking_loop).start()

    def stop_hand_tracking(self):
        self.is_tracking = False
        self.root.destroy()
