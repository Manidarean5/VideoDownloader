import tkinter as tk
from tkinter import Toplevel, messagebox
import yt_dlp
import configparser
import os
from tqdm import tqdm
import threading

# Función para guardar las opciones en el archivo config.ini
def guardar_config(entrada_formato, entrada_ruta):
    opciones['Opciones']['format'] = entrada_formato.get()
    opciones['Opciones']['ruta_archivo'] = entrada_ruta.get()
    
    with open('config.ini', 'w') as configfile:
        opciones.write(configfile)

# Función para cargar las opciones desde el archivo config.ini
def cargar_config(entrada_formato, entrada_ruta):
    try:
        opciones.read('config.ini')
        entrada_formato.insert(0, opciones['Opciones']['format'])
        entrada_ruta.insert(0, opciones['Opciones']['ruta_archivo'])
    except FileNotFoundError:
        pass

# Función para abrir la ventana de configuración
def abrir_ventana_config():
    ventana_config = Toplevel(ventana)
    ventana_config.title("Configuración")

    # Etiqueta y campo de entrada para el formato
    etiqueta_formato = tk.Label(ventana_config, text="Formato de descarga:")
    etiqueta_formato.pack()
    entrada_formato = tk.Entry(ventana_config, width=40)
    entrada_formato.pack()

    # Etiqueta y campo de entrada para la ruta del archivo
    etiqueta_ruta = tk.Label(ventana_config, text="Ruta del archivo:")
    etiqueta_ruta.pack()
    entrada_ruta = tk.Entry(ventana_config, width=40)
    entrada_ruta.pack()

    # Botón para guardar la configuración
    boton_configuracion = tk.Button(ventana_config, text="Guardar Configuración", command=lambda: guardar_config(entrada_formato, entrada_ruta))
    boton_configuracion.pack()

    # Cargar configuración existente o crear un archivo config.ini vacío
    cargar_config(entrada_formato, entrada_ruta)

# Función para mostrar la ventana de espera
def mostrar_ventana_espera():
    global ventana_espera
    ventana_espera = Toplevel(ventana)
    ventana_espera.title("Esperando Descarga")
    etiqueta_espera = tk.Label(ventana_espera, text="Descargando... Por favor, espere.")
    etiqueta_espera.pack()

# Función para ocultar la ventana de espera
def ocultar_ventana_espera():
    global ventana_espera
    if ventana_espera:
        ventana_espera.destroy()

# Función para descargar el video en un hilo separado
def descargar_video():
    url = entrada_url.get()
    formato = opciones['Opciones']['format']
    ruta_archivo = opciones['Opciones']['ruta_archivo']
    
    # Verificar si la ruta del archivo es válida
    if ruta_archivo and not os.path.isdir(ruta_archivo):
        messagebox.showerror("Error", "La ruta del archivo no es válida.")
        return
    
    mostrar_ventana_espera()  # Mostrar la ventana de espera
    
    # Configurar la opción outtmpl para que el nombre del archivo sea automático
    ydl_opts = {
        'format': formato,
        'outtmpl': os.path.join(ruta_archivo, '%(title)s.%(ext)s') if ruta_archivo else '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            mostrar_error(str(e))
        finally:
            ocultar_ventana_espera()  # Ocultar la ventana de espera cuando la descarga finaliza

# Función para actualizar la etiqueta de progreso y velocidad
def actualizar_etiqueta_progreso(progreso, velocidad):
    estado_label.config(text=f"Descargando... Progreso: {progreso}% Velocidad: {velocidad:.2f} MB/s")

# Función para mostrar una ventana con el mensaje de error
def mostrar_error(mensaje):
    messagebox.showerror("Error", mensaje)

# Función para manejar el progreso de descarga
def progress_hook(data):
    if data['status'] == 'downloading':
        total_bytes = int(data['total_bytes'])
        downloaded_bytes = int(data['downloaded_bytes'])
        speed = float(data['speed']) / 1024 / 1024  # Convertir a MB/s
        progreso = int((downloaded_bytes / total_bytes) * 100)
        actualizar_etiqueta_progreso(progreso, speed)

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Descargar Video de YouTube")

# Botón para abrir la ventana de configuración
boton_config = tk.Button(ventana, text="Configuración", command=abrir_ventana_config)
boton_config.grid(row=0, column=0, sticky="nw")

# Etiqueta y campo de entrada para la URL
etiqueta_url = tk.Label(ventana, text="Introduce la URL de YouTube:")
etiqueta_url.grid(row=1, column=0, columnspan=2)
entrada_url = tk.Entry(ventana, width=40)
entrada_url.grid(row=1, column=2, columnspan=2)

# Botón para iniciar la descarga
boton_descargar = tk.Button(ventana, text="Descargar", command=lambda: threading.Thread(target=descargar_video).start())
boton_descargar.grid(row=2, column=0, columnspan=4)

# Etiqueta para mostrar el estado de la descarga
estado_label = tk.Label(ventana, text="")
estado_label.grid(row=3, column=0, columnspan=4)

# Configuración de opciones usando configparser
opciones = configparser.ConfigParser()
opciones['Opciones'] = {
    'format': 'best',
    'ruta_archivo': '',
}

ventana.mainloop()
