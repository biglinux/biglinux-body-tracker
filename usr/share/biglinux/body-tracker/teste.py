import tkinter as tk
import math

def create_tooltip(text, x, y):
    tooltip = tk.Toplevel(root)
    tooltip.transient(root)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{x}+{y}")

    label = tk.Label(tooltip, text=text, font=("Arial", 12), bg="white", borderwidth=2, relief="solid")
    label.pack()

    return tooltip, label

def circular_menu(event, options, action=None):
    radius = 100
    angle = 360 / len(options)

    tooltips = []
    labels = []

    for i, (display_name, _) in enumerate(options):
        x = event.x_root + radius * 0.8 * math.sin(math.radians(i * angle))
        y = event.y_root - radius * 0.8 * math.cos(math.radians(i * angle))

        tooltip, label = create_tooltip(display_name, int(x), int(y))
        tooltips.append(tooltip)
        labels.append(label)

    center_tooltip, center_label = create_tooltip("", event.x_root, event.y_root)
    center_label.config(width=2, height=1)
    tooltips.append(center_tooltip)
    labels.append(center_label)

    def on_motion(event):
        x, y = root.winfo_pointerx(), root.winfo_pointery()
        distances = [(math.sqrt((x - (tooltip.winfo_rootx() + label.winfo_width() // 2)) ** 2 + (y - (tooltip.winfo_rooty() + label.winfo_height() // 2)) ** 2), i) for i, (tooltip, label) in enumerate(zip(tooltips, labels))]
        _, selected_index = min(distances)
        
        for i, label in enumerate(labels):
            if i == selected_index:
                label.config(bg="blue", fg="white")
            else:
                label.config(bg="white", fg="black")

    def on_left_release(event):
        x, y = root.winfo_pointerx(), root.winfo_pointery()
        distances = [(math.sqrt((x - (tooltip.winfo_rootx() + label.winfo_width() // 2)) ** 2 + (y - (tooltip.winfo_rooty() + label.winfo_height() // 2)) ** 2), i) for i, (tooltip, label) in enumerate(zip(tooltips, labels))]
        _, selected_index = min(distances)

        if selected_index < len(options):
            display_name, internal_name = options[selected_index]
            print(f"Opção selecionada: {display_name} ({internal_name})")
            if action:
                action(internal_name)
        else:
            print("Opção central selecionada")

        for tooltip in tooltips:
            tooltip.destroy()

    root.bind("<Motion>", on_motion)
    root.bind("<ButtonRelease-1>", on_left_release)

def sample_action(option):
    print(f"Ação executada para a opção: {option}")

root = tk.Tk()
root.geometry("800x600")
root.title("Menu Circular")

options = [
    ("Abrir navegador", "browser"),
    ("Opção 2", "option2"),
    ("Opção 3", "option3"),
    ("Opção 4", "option4"),
]

root.bind("<ButtonPress-1>", lambda event: circular_menu(event, options, sample_action))

root.mainloop()
