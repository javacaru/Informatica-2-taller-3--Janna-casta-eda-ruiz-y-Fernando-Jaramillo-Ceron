import os
import numpy as np
import pandas as pd
import cv2
import pydicom
from pathlib import Path

class ProcesadorDICOM:
    TAGS = {
        "PatientID":          "PatientID",
        "PatientName":        "PatientName",
        "StudyInstanceUID":   "StudyInstanceUID",
        "StudyDescription":   "StudyDescription",
        "StudyDate":          "StudyDate",
        "Modality":           "Modality",
        "Rows":               "Rows",
        "Columns":            "Columns",
    }

    def __init__(self, directorio_entrada: str, directorio_salida: str = "output"):
        self.directorio_entrada = Path(directorio_entrada)
        self.directorio_salida = Path(directorio_salida)
        self.directorio_salida.mkdir(exist_ok=True)
        self.datasets: list[pydicom.Dataset] = []
        self.df: pd.DataFrame = pd.DataFrame()

    # Carga de archivos DICOM 
    def cargar_archivos(self) -> None:
    #Escanea el directorio y carga todos los archivos DICOM válidos
        archivos = list(self.directorio_entrada.rglob("*"))
        print(f"Escaneando {len(archivos)} archivo(s) en '{self.directorio_entrada}'...")
        for ruta in archivos:
            if ruta.is_file():
                try:
                    ds = pydicom.dcmread(str(ruta))
                    ds.filepath = str(ruta) # atributo extra para referencia al archivo original
                    self.datasets.append(ds)
                except Exception:
                    pass # no es un DICOM válido, se ignora
        print(f"  → {len(self.datasets)} archivo(s) DICOM cargado(s).")

    # Extracción y estructuración de metadatos
    def extraer_metadatos(self) -> None:
    #Extrae los tags DICOM y construye el DataFrame
        filas = []
        for ds in self.datasets:
            fila = {"Archivo": Path(ds.filepath).name}
            for col, tag in self.TAGS.items():
                valor = getattr(ds, tag, None)
                fila[col] = str(valor) if valor is not None else "N/A"
            filas.append(fila)
        self.df = pd.DataFrame(filas)
        print(f"Metadatos extraídos: {len(self.df)} fila(s), {len(self.df.columns)} columna(s).")

    # Análisis NumPy 
    def calcular_intensidad_promedio(self) -> None:
    #Agrega la columna IntensidadPromedio al DataFrame
        promedios = []
        for ds in self.datasets:
            try:
                promedios.append(round(float(np.mean(ds.pixel_array)), 4))
            except Exception:
                promedios.append(None)
        self.df["IntensidadPromedio"] = promedios

    # ── 4.5 Procesamiento OpenCV ───────────────────────────────────────────────
    def procesar_imagenes(self, canny_th1: int = 50, canny_th2: int = 150) -> None:
    #Para cada imagen DICOM:
        #1. Normaliza a uint8 [0-255]
        #2. Ecualiza el histograma
        #3. Detecta bordes con Canny
        #4. Guarda ambas imágenes procesadas en el directorio de salida
        #Justificación de umbrales Canny: th1=50 (borde débil), th2=150 (borde fuerte).
        #Relación 1:3 recomendada; equilibra sensibilidad y ruido en imágenes médicas.
        procesadas = 0
        for ds in self.datasets:
            try:
                arr = ds.pixel_array.astype(np.float32)
            except Exception:
                continue  # sin datos de píxeles (SR, PR, etc.)

            # Normalización a uint8
            arr_min, arr_max = arr.min(), arr.max()
            if arr_max == arr_min:
                continue
            img_uint8 = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)

            # Si la imagen tiene más de 2 dims (e.g. RGB), tomar primer canal
            if img_uint8.ndim == 3:
                img_uint8 = img_uint8[..., 0]

            # Ecualización del histograma
            img_eq = cv2.equalizeHist(img_uint8)

            # Detección de bordes con Canny
            img_canny = cv2.Canny(img_eq, canny_th1, canny_th2)

            # Guardado
            nombre_base = Path(ds.filepath).stem
            cv2.imwrite(str(self.directorio_salida / f"{nombre_base}_equalizado.png"), img_eq)
            cv2.imwrite(str(self.directorio_salida / f"{nombre_base}_bordes.png"), img_canny)
            procesadas += 1

        print(f"Imágenes procesadas y guardadas: {procesadas} en '{self.directorio_salida}'.")

    # Exportar DataFrame a CSV 
    def exportar_csv(self, nombre: str = "metadatos_dicom.csv") -> None:
        ruta = self.directorio_salida / nombre
        self.df.to_csv(ruta, index=False)
        print(f"DataFrame exportado → {ruta}")

    def mostrar_resumen(self) -> None:
        print("\n── Resumen del DataFrame ──────────────────────────────────")
        print(self.df.to_string(index=False))
