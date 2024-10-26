import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
from datetime import datetime

class GIFExtractorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Extractor de datos de GIF")
        
        self.label = tk.Label(master, text="Ingrese la dirección al archivo, o carpeta:")
        self.label.pack()

        self.path_entry = tk.Entry(master, width=50)
        self.path_entry.pack()

        self.browse_button = tk.Button(master, text="Buscar", command=self.browse)
        self.browse_button.pack()

        self.extract_button = tk.Button(master, text="Extraer GIFs", command=self.extract_gifs)
        self.extract_button.pack()

        self.gif_listbox = Listbox(master)
        self.gif_listbox.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.gif_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.gif_listbox.yview)

        self.gif_listbox.bind('<<ListboxSelect>>', self.show_gif_info)

        # Documento que guarda la información
        self.output_file = "gif_info.txt"
        with open(self.output_file, "w") as f:
            f.write("Información extraída:\n\n")

    #Permite leer la dirección a una carpeta
    def browse(self):
        path = filedialog.askdirectory()  
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def extract_gifs(self):
        path = self.path_entry.get()
        if os.path.isfile(path) and path.lower().endswith('.gif'):
            self.extract_gif_info(path)
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.lower().endswith('.gif'):
                    self.extract_gif_info(os.path.join(path, filename))
        else:
            messagebox.showerror("Error", "Dirección no válida.")


    def extract_gif_info(self, gif_path):
        try:
            with open(gif_path, 'rb') as f:
                header = f.read(6)
                if header[:3] != b'GIF':
                    messagebox.showerror("Error", f"{gif_path} no es un archivo GIF.")
                    return

                version = header[3:6].decode('ascii')
                f.seek(6)
                width, height = struct.unpack('<HH', f.read(4))
                packed = f.read(1)
            
                # Tabla de información de color
                color_table_flag = (packed[0] & 0b10000000) >> 7
                color_resolution = ((packed[0] & 0b01110000) >> 4) + 1
                color_table_size = 2 ** ((packed[0] & 0x07) + 1) if color_table_flag else 0
                background_color_index = f.read(1)[0] if color_table_flag else None
                
                # Información estática del GIF
                compression_type = "LZW"
                numeric_format = "Binary"
                
                f.seek(13)
                num_images = 0
                comments = []

                # Cuenta el número de imágenes y extrae comentarios
                while True:
                    block = f.read(1)
                    if not block:
                        break
                    if block == b',':
                        num_images += 1
                        f.seek(9, 1)  #salta el descriptor de imagen
                    elif block == b';':
                        break
                    elif block == b'!':  
                        ext_label = f.read(1)
                        if ext_label == b'\xFF':  # Extensión
                        # Identificador
                            app_id = f.read(11)
                            if app_id == b'NETSCAPE2.0':
                                f.read(8)  
                            else:
                            # Lee el Block de comentarios
                                while True:
                                    block_size = ord(f.read(1))
                                    if block_size == 0:
                                        break  # Termina el Block de comentarios
                                    comment = f.read(block_size).decode('latin-1')  # Usa latin-1 encoding
                                    comments.append(comment)

                creation_date = datetime.fromtimestamp(os.path.getctime(gif_path)).strftime('%Y-%m-%d %H:%M:%S')
                modification_date = datetime.fromtimestamp(os.path.getmtime(gif_path)).strftime('%Y-%m-%d %H:%M:%S')

                gif_info = {
                    "File Name": os.path.basename(gif_path),
                    "Version": version,
                    "Width": width,
                    "Height": height,
                    "Color Table Size": color_table_size,
                    "Number of Colors": color_table_size,
                    "Compression Type": compression_type,
                    "Numeric Format": numeric_format,
                    "Background Color Index": background_color_index,
                    "Number of Images": num_images,
                    "Creation Date": creation_date,
                    "Modification Date": modification_date,
                    "Comments": "\n".join(comments) if comments else "No comments found"
                }

                self.gif_listbox.insert(tk.END, gif_info["File Name"])
                self.save_gif_info(gif_info)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_gif_info(self, event):
        selected_index = self.gif_listbox.curselection()
        if selected_index:
            gif_name = self.gif_listbox.get(selected_index)
            with open(self.output_file, "r") as f:
                content = f.read()
                # Información del archivo específico
                start_index = content.find(f"File Name: {gif_name}")
                end_index = content.find("\n\n", start_index) + 2
                gif_info = content[start_index:end_index] if start_index != -1 else "Información no disponible."
            messagebox.showinfo("Información del GIF", gif_info)

    def save_gif_info(self, gif_info):
        with open(self.output_file, "a") as f:
            f.write(f"File Name: {gif_info['File Name']}\n")
            f.write(f"Version: {gif_info['Version']}\n")
            f.write(f"Width: {gif_info['Width']}\n")
            f.write(f"Height: {gif_info['Height']}\n")
            f.write(f"Color Table Size: {gif_info['Color Table Size']}\n")
            f.write(f"Number of Colors: {gif_info['Number of Colors']}\n")
            f.write(f"Compression Type: {gif_info['Compression Type']}\n")
            f.write(f"Numeric Format: {gif_info['Numeric Format']}\n")
            f.write(f"Background Color Index: {gif_info['Background Color Index']}\n")
            f.write(f"Number of Images: {gif_info['Number of Images']}\n")
            f.write(f"Creation Date: {gif_info['Creation Date']}\n")
            f.write(f"Modification Date: {gif_info['Modification Date']}\n")
            f.write(f"Comments: {gif_info['Comments']}\n")
            f.write("\n\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = GIFExtractorApp(root)
    root.mainloop()