import sys
from procesador_dicom import ProcesadorDICOM

def main():
    directorio_entrada = sys.argv[1] if len(sys.argv) > 1 else "dicom_files"
    directorio_salida  = sys.argv[2] if len(sys.argv) > 2 else "output"

    proc = ProcesadorDICOM(directorio_entrada, directorio_salida)

    proc.cargar_archivos()
    if not proc.datasets:
        print("No se encontraron archivos DICOM. Verifica el directorio de entrada.")
        return

    proc.extraer_metadatos()
    proc.calcular_intensidad_promedio()
    proc.procesar_imagenes()
    proc.exportar_csv()
    proc.mostrar_resumen()


if __name__ == "__main__":
    main()
