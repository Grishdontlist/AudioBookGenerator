import pyttsx3
import PyPDF2
import re
from tkinter.filedialog import *
from tkinter import messagebox, ttk
import tkinter as tk
from threading import Thread
import time


class AudioBookGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.current_page = 0
        self.is_paused = False
        self.is_stopped = False
        self.total_pages = 0
        self.reading_thread = None

    def clean_text(self, text):
        # clean_text
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"([.!?])", r"\1. ", text)
        text = re.sub(r"[*_~]", "", text)
        text = re.sub(r'"(\w)', r'" \1', text)
        text = text.replace("Mr.", "Mister")
        text = text.replace("Mrs.", "Misses")
        text = text.replace("Dr.", "Doctor")
        return text.strip()

    def create_gui(self):
        # create_gui
        self.root = tk.Tk()
        self.root.title("AudioBook Generator")
        self.root.geometry("560x420")

        frame = ttk.LabelFrame(self.root, text="Voice Settings", padding="10")
        frame.pack(fill="x", padx=10, pady=5)

        voices = self.engine.getProperty("voices")
        self.voice_var = tk.StringVar()

        for i, voice in enumerate(voices):
            ttk.Radiobutton(
                frame,
                text=f"Voice {i+1}: {voice.name}",
                variable=self.voice_var,
                value=str(i),
            ).pack(side="left", padx=6, pady=2)

        if voices:
            self.voice_var.set("0")

        
        # Speed control
        speed_frame = ttk.LabelFrame(self.root, text="Reading Speed", padding="10")
        speed_frame.pack(fill="x", padx=10, pady=5)

        self.speed_var = tk.IntVar(value=150)
        speed_scale = ttk.Scale(
            speed_frame, from_=100, to=300, variable=self.speed_var, orient="horizontal"
        )
        speed_scale.pack(fill="x")

        
        # Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="Select PDF", command=self.select_pdf).pack(
            side="left", padx=5
        )
        ttk.Button(control_frame, text="Start", command=self.start_reading).pack(
            side="left", padx=5
        )
        ttk.Button(control_frame, text="Pause/Resume", command=self.pause_resume).pack(
            side="left", padx=5
        )
        ttk.Button(control_frame, text="Stop", command=self.stop_reading).pack(
            side="left", padx=5
        )

        
        # Jump to page controls
        ttk.Label(control_frame, text="Go to page:").pack(side="left", padx=(10, 2))
        self.goto_var = tk.StringVar()
        ttk.Entry(control_frame, width=6, textvariable=self.goto_var).pack(
            side="left", padx=2
        )
        ttk.Button(control_frame, text="Go", command=self.goto_page).pack(side="left", padx=5)

        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to start...")
        ttk.Label(self.root, textvariable=self.progress_var).pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def select_pdf(self):
        # select_pdf
        self.book_path = askopenfilename(
            title="Select PDF File", filetypes=[("PDF files", "*.pdf")]
        )
        if self.book_path:
            try:
                self.pdfreader = PyPDF2.PdfReader(self.book_path)
                self.total_pages = len(self.pdfreader.pages)
                self.progress_var.set(f"Loaded PDF: {self.total_pages} pages")
                self.progress_bar["maximum"] = self.total_pages
            except Exception as e:
                messagebox.showerror("Error", f"Error loading PDF: {str(e)}")

    def start_reading(self):
        # start_reading
        if not hasattr(self, "book_path"):
            messagebox.showinfo("Info", "Please select a PDF file first")
            return

        
        # Configure engine with selected settings
        try:
            voice_index = int(self.voice_var.get())
        except Exception:
            voice_index = 0
        voices = self.engine.getProperty("voices")
        if voices:
            self.engine.setProperty("voice", voices[voice_index].id)
        self.engine.setProperty("rate", self.speed_var.get())

        
        # Reset flags
        self.is_stopped = False
        self.is_paused = False

        
        # Start reading in a separate thread
        t = Thread(target=self.read_book)
        t.daemon = True
        self.reading_thread = t
        t.start()

    def read_book(self):
        # read_book
        try:
            for num in range(self.current_page, self.total_pages):
                if self.is_stopped:
                    break

                while self.is_paused:
                    time.sleep(0.1)
                    if self.is_stopped:
                        break

                page = self.pdfreader.pages[num]
                text = page.extract_text() or ""
                if text.strip():
                    text = self.clean_text(text)

                    self.current_page = num
                    self.progress_var.set(
                        f"Reading page {num + 1} of {self.total_pages}"
                    )
                    self.progress_bar["value"] = num + 1
                    try:
                        self.root.update_idletasks()
                    except Exception:
                        pass

                    self.engine.say(text)
                    self.engine.runAndWait()

            if not self.is_stopped:
                self.progress_var.set("Finished reading!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # mark reading thread finished
            self.reading_thread = None

    def goto_page(self):
        # goto_page
        if not hasattr(self, "book_path"):
            messagebox.showinfo("Info", "Please select a PDF file first")
            return

        try:
            page_num = int(self.goto_var.get())
        except Exception:
            messagebox.showerror("Error", "Please enter a valid page number")
            return

        if page_num < 1 or page_num > self.total_pages:
            messagebox.showerror(
                "Error", f"Page number must be between 1 and {self.total_pages}"
            )
            return

        
        # Stop current reading and interrupt speech
        self.is_stopped = True
        self.is_paused = False
        try:
            self.engine.stop()
        except Exception:
            pass

        
        # Give the reader loop a short moment to exit
        time.sleep(0.05)

        
        # Set new page and restart reading
        self.current_page = page_num - 1
        self.progress_var.set(f"Jumped to page {page_num}")
        self.progress_bar["value"] = page_num
        self.is_stopped = False

        # start new reading thread
        t = Thread(target=self.read_book)
        t.daemon = True
        self.reading_thread = t
        t.start()

    def pause_resume(self):
        # pause_resume
        self.is_paused = not self.is_paused
        status = "Paused" if self.is_paused else "Resumed"
        self.progress_var.set(f"{status} at page {self.current_page + 1}")

    def stop_reading(self):
        # stop_reading
        self.is_stopped = True
        self.is_paused = False
        self.current_page = 0
        self.progress_var.set("Stopped reading")
        self.progress_bar["value"] = 0

    def on_closing(self):
        # on_closing
        self.is_stopped = True
        self.root.destroy()


if __name__ == "__main__":
    app = AudioBookGenerator()
    app.create_gui()
