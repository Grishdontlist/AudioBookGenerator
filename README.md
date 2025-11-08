# 📚 AudioBook Generator (PDF to Speech)

A simple **AudioBook Generator** that converts PDF files into spoken audio using Python.  
The application provides a GUI where the user can:

- Upload a PDF
- Choose different voice options (from your system voices)
- Adjust reading speed
- Start / Pause / Resume / Stop reading
- Jump to a specific page

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| Select PDF | Choose any PDF to read aloud |
| Voice selection | Lets you pick from available system voices |
| Adjustable speed | Change reading speed (words per minute) |
| Pause / Resume | Pause and continue audio |
| Stop reading | Stop reading anytime |
| Jump to page | Enter a page number and jump instantly |
| Shows progress | Progress bar and status message while reading |

---

## 🧠 How It Works

This project uses:

- `PyPDF2` — to extract text from PDF files
- `pyttsx3` — offline text-to-speech conversion
- `tkinter` — to build the graphical interface
- `threading` — to prevent UI freezing during reading

The program reads PDF text **page by page**, cleans it for better text-to-speech output, and speaks it aloud.

