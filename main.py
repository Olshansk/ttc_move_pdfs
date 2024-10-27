import argparse
import difflib
import os
import shutil

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


def main(source_folder, compare_folder, dest_folder):
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
    with open("output.txt", "w") as f:
        for source_pdf, compare_pdf, dest_pdf in matches:
            f.write(f"Source: {source_pdf}\n")
            f.write(f"Compare: {compare_pdf}\n")
            f.write(f"Destination: {dest_pdf}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare and move PDF files.")
    parser.add_argument("source_folder", help="Path to the source folder.")
    parser.add_argument("compare_folder", help="Path to the compare folder.")
    parser.add_argument("dest_folder", help="Path to the destination folder.")

    args = parser.parse_args()

    main(args.source_folder, args.compare_folder, args.dest_folder)
