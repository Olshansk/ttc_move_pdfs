import difflib
import os
import shutil
import threading

# import tkinter
import tkinter as tk
from tkinter import filedialog, messagebox

# import _tkinter
from PyPDF2 import PdfReader


def get_pdf_files(folder):
    pdf_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    return pdf_files


def get_pdf_page_count(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None


def compare_and_move(source_folder, compare_folder, dest_folder, output_file):
    source_pdfs = get_pdf_files(source_folder)
    compare_pdfs = get_pdf_files(compare_folder)

    compare_pdf_names = {os.path.splitext(os.path.basename(path))[0]: path for path in compare_pdfs}

    matches = []

    for source_pdf in source_pdfs:
        source_name = os.path.splitext(os.path.basename(source_pdf))[0]
        best_match = None
        highest_ratio = 0

        for compare_name in compare_pdf_names:
            ratio = difflib.SequenceMatcher(None, source_name, compare_name).ratio()
            if ratio > 0.9 and ratio > highest_ratio:
                highest_ratio = ratio
                best_match = compare_name

        if best_match:
            source_pages = get_pdf_page_count(source_pdf)
            compare_pages = get_pdf_page_count(compare_pdf_names[best_match])

            if source_pages is not None and compare_pages is not None:
                if source_pages == compare_pages:
                    dest_path = os.path.join(dest_folder, os.path.basename(source_pdf))
                    shutil.move(source_pdf, dest_path)
                    matches.append((source_pdf, compare_pdf_names[best_match], dest_path))
                    print(f"Moved {source_pdf} to {dest_path}")

    # Write matches to output file
    with open(output_file, "w") as f:
        for source_pdf, compare_pdf, dest_pdf in matches:
            f.write(f"Source: {source_pdf}\n")
            f.write(f"Compare: {compare_pdf}\n")
            f.write(f"Destination: {dest_pdf}\n\n")

    messagebox.showinfo("Process Completed", f"Files have been moved. See {output_file} for details.")


def start_process():
    source_folder = source_entry.get()
    compare_folder = compare_entry.get()
    dest_folder = dest_entry.get()
    output_file = os.path.join(os.getcwd(), "output.txt")

    if not all([source_folder, compare_folder, dest_folder]):
        messagebox.showwarning("Input Error", "Please select all three folders.")
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    threading.Thread(target=compare_and_move, args=(source_folder, compare_folder, dest_folder, output_file)).start()


def select_source_folder():
    folder_selected = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder_selected)


def select_compare_folder():
    folder_selected = filedialog.askdirectory()
    compare_entry.delete(0, tk.END)
    compare_entry.insert(0, folder_selected)


def select_dest_folder():
    folder_selected = filedialog.askdirectory()
    dest_entry.delete(0, tk.END)
    dest_entry.insert(0, folder_selected)


# Create the main window
root = tk.Tk()
root.title("PDF Compare and Move")

# Source Folder
source_label = tk.Label(root, text="Source Folder:")
source_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
source_entry = tk.Entry(root, width=50)
source_entry.grid(row=0, column=1, padx=10, pady=5)
source_button = tk.Button(root, text="Browse...", command=select_source_folder)
source_button.grid(row=0, column=2, padx=10, pady=5)

# Compare Folder
compare_label = tk.Label(root, text="Compare Folder:")
compare_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
compare_entry = tk.Entry(root, width=50)
compare_entry.grid(row=1, column=1, padx=10, pady=5)
compare_button = tk.Button(root, text="Browse...", command=select_compare_folder)
compare_button.grid(row=1, column=2, padx=10, pady=5)

# Destination Folder
dest_label = tk.Label(root, text="Destination Folder:")
dest_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
dest_entry = tk.Entry(root, width=50)
dest_entry.grid(row=2, column=1, padx=10, pady=5)
dest_button = tk.Button(root, text="Browse...", command=select_dest_folder)
dest_button.grid(row=2, column=2, padx=10, pady=5)

# Start Button
start_button = tk.Button(root, text="Start", command=start_process)
start_button.grid(row=3, column=1, padx=10, pady=20)

root.mainloop()
