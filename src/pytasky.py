import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
from datetime import datetime, timedelta
import os
import json
import csv
from sqlalchemy import and_
from models import Task, get_session  # Import from models.py


class PyTaskyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTasky")
        self.root.geometry("600x400")

        # Set app icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except tk.TclError as e:
                print(f"Error setting icon: {e}")

        # Load version
        with open(os.path.join(os.path.dirname(__file__), "version.txt"), "r") as f:
            self.version = f.read().strip()

        # Timer variables
        self.running = False
        self.custom_pomodoro = 25
        self.time_left = self.custom_pomodoro * 60
        self.pomodoro_count = 0

        # GUI Setup
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Timer Tab (Active Tasks)
        timer_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(timer_frame, text="Active Tasks")

        self.time_label = ttk.Label(
            timer_frame, text=f"{self.custom_pomodoro:02d}:00", font=("Helvetica", 48)
        )
        self.time_label.pack()

        button_frame = ttk.Frame(timer_frame, padding="10")
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="Start", command=self.start_timer).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Stop", command=self.stop_timer).pack(
            side="left", padx=5
        )
        ttk.Button(
            button_frame, text="Short Break (5m)", command=lambda: self.set_break(5)
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Long Break (15m)", command=lambda: self.set_break(15)
        ).pack(side="left", padx=5)

        # Custom Pomodoro setting
        custom_frame = ttk.Frame(timer_frame, padding="5")
        custom_frame.pack(fill="x")
        ttk.Label(custom_frame, text="Pomodoro (min):").pack(side="left")
        self.custom_entry = tk.Entry(custom_frame, width=5)
        self.custom_entry.insert(0, str(self.custom_pomodoro))
        self.custom_entry.pack(side="left", padx=5)
        ttk.Button(custom_frame, text="Set", command=self.set_custom_pomodoro).pack(
            side="left"
        )

        # Add Task Frame
        input_frame = ttk.LabelFrame(timer_frame, text="Add Task", padding="10")
        input_frame.pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(input_frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Notes:").grid(row=1, column=0, sticky="w")
        self.notes_entry = tk.Entry(input_frame)
        self.notes_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Tag:").grid(row=2, column=0, sticky="w")
        self.tag_entry = tk.Entry(input_frame)
        self.tag_entry.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Status:").grid(row=3, column=0, sticky="w")
        self.status_combo = ttk.Combobox(
            input_frame,
            values=[
                "todo",
                "in-progress",
                "blocked",
                "testing",
                "verify",
                "done",
                "cancelled",
            ],
        )
        self.status_combo.set("todo")
        self.status_combo.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(
            row=4, column=1, pady=5, sticky="e"
        )

        # Tasks Frame
        tasks_frame = ttk.LabelFrame(
            timer_frame, text="Tasks (Double-click to edit)", padding="10"
        )
        tasks_frame.pack(fill="both", expand=True)

        self.task_list = tk.Listbox(tasks_frame)
        self.task_list.pack(fill="both", expand=True)
        self.task_list.bind("<Double-1>", self.open_edit_window)
        self.update_task_list()

        # Done Tasks Tab
        done_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(done_frame, text="Done Tasks")

        self.done_list = tk.Listbox(done_frame)
        self.done_list.pack(fill="both", expand=True)
        self.update_done_list()

        # Report Tab
        report_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(report_frame, text="Reports")

        # Filter Frame (Reports Frame)
        filter_frame = ttk.LabelFrame(report_frame, text="Report Filters", padding="10")
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Start Date (YYYY-MM-DD):").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.start_date_entry = tk.Entry(filter_frame)
        default_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.start_date_entry.insert(0, default_start)
        self.start_date_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(filter_frame, text="End Date (YYYY-MM-DD):").grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.end_date_entry = tk.Entry(filter_frame)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(filter_frame, text="Statuses (Ctrl+Click for multiple):").grid(
            row=2, column=0, sticky="w", pady=2
        )
        status_frame = ttk.Frame(filter_frame)
        status_frame.grid(row=2, column=1, sticky="ew", padx=5)

        self.status_filter = tk.Listbox(status_frame, selectmode="multiple", height=5)
        statuses = [
            "todo",
            "in-progress",
            "blocked",
            "testing",
            "verify",
            "done",
            "cancelled",
        ]
        for status in statuses:
            self.status_filter.insert(tk.END, status)
        for i in range(len(statuses)):
            self.status_filter.select_set(i)
        self.status_filter.pack(side=tk.LEFT, fill="y")

        scrollbar = tk.Scrollbar(
            status_frame, orient="vertical", command=self.status_filter.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.status_filter.config(yscrollcommand=scrollbar.set)

        ttk.Button(
            filter_frame,
            text="Generate JSON Report",
            command=lambda: self.generate_report("json"),
        ).grid(row=3, column=0, pady=5)
        ttk.Button(
            filter_frame,
            text="Generate CSV Report",
            command=lambda: self.generate_report("csv"),
        ).grid(row=3, column=1, pady=5)

        # About Tab
        about_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(about_frame, text="About")

        logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
        if os.path.exists(logo_path):
            logo = tk.PhotoImage(file=logo_path)
            self.root.update()
            window_width = self.root.winfo_width()
            logo_width = int(window_width * 0.2)
            original_width = logo.width()
            original_height = logo.height()
            logo_height = int(logo_width * original_height / original_width)
            logo = logo.subsample(
                int(original_width / logo_width), int(original_height / logo_height)
            )
            ttk.Label(about_frame, image=logo).pack(pady=10)
            about_frame.image = logo

        about_text = f"""PyTasky v{self.version}
A Pomodoro time management application for your tasks
Built with Python
Developed by Elephanta Technology and Design Inc.
https://github.com/elephantatech/pyTasky
"""
        ttk.Label(about_frame, text=about_text, justify="center").pack(pady=10)

    def set_custom_pomodoro(self):
        try:
            minutes = int(self.custom_entry.get())
            if minutes > 0:
                self.custom_pomodoro = minutes
                self.time_left = minutes * 60
                self.time_label.config(text=f"{minutes:02d}:00")
            else:
                messagebox.showwarning("Input Error", "Please enter a positive number!")
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number!")

    def update_timer(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
        elif self.running and self.time_left == 0:
            self.running = False
            self.pomodoro_count += 1
            messagebox.showinfo("PyTasky", "Time's up! Take a break.")
            self.update_status_to_done()

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()

    def stop_timer(self):
        self.running = False

    def set_break(self, minutes):
        self.running = False
        self.time_left = minutes * 60
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Input Error", "Title is required!")
            return

        notes = self.notes_entry.get().strip()
        tag = self.tag_entry.get().strip()
        status = self.status_combo.get()
        now = datetime.now()

        session = get_session()
        task = Task(
            title=title,
            notes=notes,
            tag=tag,
            status=status,
            created_at=now,
            last_updated=now,
        )
        if status in ["done", "cancelled"]:
            task.completed_at = now
        session.add(task)
        session.commit()
        session.close()

        self.clear_input_fields()
        self.update_task_list()
        self.update_done_list()

    def open_edit_window(self, event):
        selected = self.task_list.curselection()
        if not selected:
            return

        task_index = selected[0]
        task_text = self.task_list.get(task_index)
        task_id = int(task_text.split(".")[0])

        session = get_session()
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            session.close()
            return

        # Create popup window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Task {task_id}")
        edit_window.geometry("300x350")

        # Title
        ttk.Label(edit_window, text="Title:").pack(pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.insert(0, task.title)
        title_entry.pack(fill="x", padx=10)

        # Notes
        ttk.Label(edit_window, text="Notes:").pack(pady=5)
        notes_entry = tk.Entry(edit_window)
        notes_entry.insert(0, task.notes or "")
        notes_entry.pack(fill="x", padx=10)

        # Tag
        ttk.Label(edit_window, text="Tag:").pack(pady=5)
        tag_entry = tk.Entry(edit_window)
        tag_entry.insert(0, task.tag or "")
        tag_entry.pack(fill="x", padx=10)

        # Status
        ttk.Label(edit_window, text="Status:").pack(pady=5)
        status_combo = ttk.Combobox(
            edit_window,
            values=[
                "todo",
                "in-progress",
                "blocked",
                "testing",
                "verify",
                "done",
                "cancelled",
            ],
        )
        status_combo.set(task.status)
        status_combo.pack(fill="x", padx=10)

        # Created At (read-only)
        ttk.Label(edit_window, text="Created At:").pack(pady=5)
        created_at_label = ttk.Label(
            edit_window,
            text=(
                task.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if task.created_at
                else "N/A"
            ),
        )
        created_at_label.pack()

        # Last Updated (read-only)
        ttk.Label(edit_window, text="Last Updated:").pack(pady=5)
        last_updated_label = ttk.Label(
            edit_window,
            text=(
                task.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                if task.last_updated
                else "N/A"
            ),
        )
        last_updated_label.pack()

        # Save button
        def save_changes():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showwarning("Input Error", "Title is required!")
                return

            new_notes = notes_entry.get().strip()
            new_tag = tag_entry.get().strip()
            new_status = status_combo.get()
            now = datetime.now()

            task.title = new_title
            task.notes = new_notes
            task.tag = new_tag
            task.status = new_status
            task.last_updated = now
            if new_status in ["done", "cancelled"]:
                task.completed_at = now
            else:
                task.completed_at = None

            session.commit()
            session.close()

            self.update_task_list()
            self.update_done_list()
            edit_window.destroy()

        ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)

    def update_status_to_done(self):
        selected = self.task_list.curselection()
        if selected:
            task_index = selected[0]
            task_text = self.task_list.get(task_index)
            task_id = int(task_text.split(".")[0])
            session = get_session()
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                now = datetime.now()
                task.status = "done"
                task.completed_at = now
                task.last_updated = now
                session.commit()
            session.close()

            self.clear_input_fields()
            self.task_list.selection_clear(0, tk.END)
            self.update_task_list()
            self.update_done_list()

    def clear_input_fields(self):
        self.title_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        self.tag_entry.delete(0, tk.END)
        self.status_combo.set("todo")

    def update_task_list(self):
        self.task_list.delete(0, tk.END)
        session = get_session()
        tasks = (
            session.query(Task)
            .filter(
                Task.status.in_(["todo", "in-progress", "blocked", "testing", "verify"])
            )
            .order_by(Task.id)
            .all()
        )
        for task in tasks:
            task_text = f"{task.id}. {task.title} [{task.status} - Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'} - Updated: {task.last_updated.strftime('%Y-%m-%d %H:%M:%S') if task.last_updated else 'N/A'}]"
            if task.tag:
                task_text += f" - {task.tag}"
            self.task_list.insert(tk.END, task_text)
        session.close()

    def update_done_list(self):
        self.done_list.delete(0, tk.END)
        session = get_session()
        tasks = (
            session.query(Task)
            .filter(Task.status.in_(["done", "cancelled"]))
            .order_by(Task.completed_at.desc())
            .all()
        )
        for task in tasks:
            task_text = f"{task.id}. {task.title} [{task.status} - Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'} - Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'} - Updated: {task.last_updated.strftime('%Y-%m-%d %H:%M:%S') if task.last_updated else 'N/A'}]"
            if task.tag:
                task_text += f" - {task.tag}"
            self.done_list.insert(tk.END, task_text)
        session.close()

    def generate_report(self, format_type):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        selected_statuses = [
            self.status_filter.get(i) for i in self.status_filter.curselection()
        ]

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Filter Error", "Dates must be in YYYY-MM-DD format!"
            )
            return

        session = get_session()
        if not selected_statuses:
            # If no statuses selected, include all tasks within date range
            tasks = (
                session.query(Task)
                .filter(and_(Task.created_at >= start_dt, Task.created_at <= end_dt))
                .all()
            )
        else:
            # Filter by selected statuses and date range
            tasks = (
                session.query(Task)
                .filter(
                    and_(
                        Task.created_at >= start_dt,
                        Task.created_at <= end_dt,
                        Task.status.in_(selected_statuses),
                    )
                )
                .all()
            )

        if not tasks:
            messagebox.showinfo("Report", "No tasks match the selected filters!")
            session.close()
            return

        # Convert tasks to a list of tuples for CSV compatibility
        task_data = [
            (
                t.id,
                t.title,
                t.notes,
                t.tag,
                t.status,
                t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None,
                (
                    t.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                    if t.completed_at
                    else None
                ),
                (
                    t.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    if t.last_updated
                    else None
                ),
            )
            for t in tasks
        ]

        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")],
            initialfile=f"pytasky_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )
        if not filename:
            session.close()
            return

        if format_type == "json":
            report = [
                {
                    "id": t.id,
                    "title": t.title,
                    "notes": t.notes,
                    "tag": t.tag,
                    "status": t.status,
                    "created_at": (
                        t.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        if t.created_at
                        else None
                    ),
                    "completed_at": (
                        t.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                        if t.completed_at
                        else None
                    ),
                    "last_updated": (
                        t.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                        if t.last_updated
                        else None
                    ),
                }
                for t in tasks
            ]
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
        elif format_type == "csv":
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "ID",
                        "Title",
                        "Notes",
                        "Tag",
                        "Status",
                        "Created At",
                        "Completed At",
                        "Last Updated",
                    ]
                )
                writer.writerows(task_data)

        messagebox.showinfo("Report", f"Report saved as {filename}")
        session.close()

    def __del__(self):
        pass  # SQLAlchemy session is closed in each method


def main():
    root = tk.Tk()
    app = PyTaskyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
