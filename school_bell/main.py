import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
from tkinter import filedialog
import schedule
import time
import threading
import pygame
import json

class SchoolBellRingerApp:
    def __init__(self, master):
        # Initialize pygame mixer
        pygame.mixer.init()

        self.master = master
        self.master.title("School Bell Ringer")

        # Set the window size and background color
        self.master.geometry("500x500")
        self.master.config(bg="#f0f0f0")

        # Initialize variables
        self.schedule = []
        self.current_period = None
        self.is_paused = False

        # Create GUI elements
        self.create_widgets()

        # Load schedule data from JSON file
        self.load_schedule()

        # Start the scheduler in a background thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def create_widgets(self):
        # Frame for adding schedule
        self.frame_add_schedule = tk.LabelFrame(self.master, text="Add Schedule", bg="#ffffff", fg="#333333", font=("Arial", 12, "bold"))
        self.frame_add_schedule.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Day select box
        tk.Label(self.frame_add_schedule, text="Day:", bg="#ffffff", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.day_select = ttk.Combobox(self.frame_add_schedule, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.day_select.grid(row=0, column=1, padx=5, pady=5)
        self.day_select.current(0)  # Default to Monday

        # Time select box
        tk.Label(self.frame_add_schedule, text="Time:", bg="#ffffff", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.time_select = ttk.Combobox(self.frame_add_schedule, values=self.get_time_options())
        self.time_select.grid(row=1, column=1, padx=5, pady=5)

        # Sound upload button
        self.sound_button = tk.Button(self.frame_add_schedule, text="Upload Sound", command=self.upload_sound, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.sound_button.grid(row=1, column=2, padx=5, pady=5)

        # List box to display schedule
        self.schedule_listbox = tk.Listbox(self.frame_add_schedule, width=50, height=10)
        self.schedule_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Horizontal row for Edit, Delete, Save buttons
        self.button_frame = tk.Frame(self.frame_add_schedule, bg="#ffffff")
        self.button_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        # Horizontally aligned Edit, Delete, Save buttons
        self.edit_button = tk.Button(self.button_frame, text="Edit", command=self.edit_schedule, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.edit_button.grid(row=0, column=0, padx=5, pady=5)
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_schedule, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        self.delete_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_schedule, bg="#009688", fg="white", font=("Arial", 10, "bold"))
        self.save_button.grid(row=0, column=2, padx=5, pady=5)

        # Pause and Stop buttons (vertically aligned)
        self.pause_button = tk.Button(self.master, text="Pause Alarm", command=self.pause_alarm, bg="#FFC107", fg="white", font=("Arial", 10, "bold"))
        self.pause_button.pack(pady=10)
        self.stop_button = tk.Button(self.master, text="Stop Alarm", command=self.stop_alarm, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        self.stop_button.pack(pady=10)

    def get_time_options(self):
        # Generate time options for combobox
        time_options = []
        for hour in range(24):
            for minute in range(0, 60, 1):
                time_options.append(f"{hour:02d}:{minute:02d}")
        return time_options

    def upload_sound(self):
        # Open file dialog to select sound file
        sound_file = filedialog.askopenfilename()
        if sound_file:
            messagebox.showinfo("Sound Uploaded", f"Sound file '{sound_file}' uploaded successfully.")
            self.sound_file = sound_file

    def save_schedule(self):
        # Get the selected day, time, and sound
        day = self.day_select.get()
        time = self.time_select.get()
        sound = self.sound_file if hasattr(self, 'sound_file') else ""

        if day and time and sound:
            # Add new schedule item to the list
            self.schedule.append({"day": day, "time": time, "sound": sound})

            # Save schedule to JSON file
            with open("schedule.json", "w") as file:
                json.dump(self.schedule, file)
            messagebox.showinfo("Schedule Saved", "Schedule saved successfully.")
            self.update_schedule_listbox()  # Update the listbox with the new schedule
        else:
            messagebox.showwarning("Incomplete Data", "Please select a day, time, and upload a sound.")

    def load_schedule(self):
        # Load schedule data from JSON file
        try:
            with open("schedule.json", "r") as file:
                self.schedule = json.load(file)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "No schedule file found. Starting with an empty schedule.")
        self.update_schedule_listbox()

    def update_schedule_listbox(self):
        # Update schedule list box
        self.schedule_listbox.delete(0, tk.END)
        for item in self.schedule:
            self.schedule_listbox.insert(tk.END, f"Day: {item['day']}, Time: {item['time']}, Sound: {item['sound']}")

    def edit_schedule(self):
        # Edit selected schedule
        selected_index = self.schedule_listbox.curselection()
        if selected_index:
            selected_item = self.schedule[selected_index[0]]
            self.edit_window = tk.Toplevel(self.master)
            self.edit_window.title("Edit Schedule")

            tk.Label(self.edit_window, text="Day:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            day_var = tk.StringVar(value=selected_item["day"])
            day_entry = ttk.Combobox(self.edit_window, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], textvariable=day_var)
            day_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(self.edit_window, text="Time:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            time_var = tk.StringVar(value=selected_item["time"])
            time_entry = ttk.Combobox(self.edit_window, values=self.get_time_options(), textvariable=time_var)
            time_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(self.edit_window, text="Sound:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            sound_var = tk.StringVar(value=selected_item["sound"])
            sound_entry = tk.Entry(self.edit_window, textvariable=sound_var)
            sound_entry.grid(row=2, column=1, padx=5, pady=5)

            save_button = tk.Button(self.edit_window, text="Save", command=lambda: self.save_edit(selected_index[0], day_entry.get(), time_entry.get(), sound_entry.get()))
            save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

    def save_edit(self, index, day, time, sound):
        self.schedule[index] = {"day": day, "time": time, "sound": sound}
        self.edit_window.destroy()
        self.update_schedule_listbox()

    def delete_schedule(self):
        # Delete selected schedule
        selected_index = self.schedule_listbox.curselection()
        if selected_index:
            self.schedule.pop(selected_index[0])
            self.update_schedule_listbox()

    def run_scheduler(self):
        # Main scheduler loop
        while True:
            current_time = time.strftime("%H:%M")
            current_day = time.strftime("%A")
            for item in self.schedule:
                if current_time == item["time"] and current_day == item["day"] and item["time"] != self.current_period:
                    self.current_period = item["time"]
                    self.trigger_bell_ring(item["sound"])
            time.sleep(1)

    def trigger_bell_ring(self, sound_file):
        # Play the bell sound
        if sound_file:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()

    def pause_alarm(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def stop_alarm(self):
        pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolBellRingerApp(root)
    root.mainloop()
