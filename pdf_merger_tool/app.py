import os
from tkinter import Tk, Frame, Button, Listbox, filedialog, messagebox, END
from tkinterdnd2 import DND_FILES, TkinterDnD
from PyPDF2 import PdfMerger

OUTPUT_DIR = "merged_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

root = TkinterDnD.Tk()
root.title("⚡ Futuristic PDF Merger")
root.geometry("700x500")
root.configure(bg="#0f172a")  

file_list = []


def drop(event):
    files = root.tk.splitlist(event.data)
    for file in files:
        if file.lower().endswith(".pdf") and file not in file_list:
            file_listbox.insert(END, os.path.basename(file))
            file_list.append(file)
        else:
            messagebox.showwarning("Invalid File", f"{file} is not a valid PDF.")


def add_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for file in files:
        if file.lower().endswith(".pdf") and file not in file_list:
            file_listbox.insert(END, os.path.basename(file))
            file_list.append(file)

def clear_files():
    file_listbox.delete(0, END)
    file_list.clear()

def merge_pdfs():
    if not file_list:
        messagebox.showerror("No Files", "Please add some PDF files first.")
        return

    output_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF File", "*.pdf")],
        initialdir=OUTPUT_DIR,
        initialfile="merged.pdf",
        title="Save Merged PDF"
    )

    if output_path:
        try:
            merger = PdfMerger()
            for pdf in file_list:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            messagebox.showinfo("Success", f"PDF saved at:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Merge Failed", str(e))


BTN_STYLE = {
    "bg": "#0ea5e9",
    "fg": "white",
    "font": ("Consolas", 11, "bold"),
    "activebackground": "#22d3ee",
    "activeforeground": "white",
    "bd": 0,
    "cursor": "hand2",
    "padx": 10,
    "pady": 5
}


Frame(root, bg="#0f172a", height=20).pack()  
title = Frame(root, bg="#0f172a")
title.pack()
title_label = Button(title, text="🧬 PDF MERGER TOOL", state="disabled", disabledforeground="#38bdf8",
                     font=("Orbitron", 20, "bold"), bg="#0f172a", bd=0)
title_label.pack()


frame = Frame(root, bg="#1e293b", bd=2, relief="groove")
frame.pack(padx=40, pady=30, fill="both", expand=True)

file_listbox = Listbox(frame, bg="#0f172a", fg="#a5f3fc", font=("Courier", 10),
                       selectbackground="#38bdf8", activestyle="none", relief="flat")
file_listbox.pack(fill="both", expand=True, padx=10, pady=10)
file_listbox.drop_target_register(DND_FILES)
file_listbox.dnd_bind('<<Drop>>', drop)


btn_frame = Frame(root, bg="#0f172a")
btn_frame.pack(pady=15)

Button(btn_frame, text="➕ Add Files", command=add_files, **BTN_STYLE).grid(row=0, column=0, padx=10)
Button(btn_frame, text="🗑 Clear", command=clear_files, **BTN_STYLE).grid(row=0, column=1, padx=10)
Button(btn_frame, text="💾 Merge & Save", command=merge_pdfs, **BTN_STYLE).grid(row=0, column=2, padx=10)


root.mainloop()
