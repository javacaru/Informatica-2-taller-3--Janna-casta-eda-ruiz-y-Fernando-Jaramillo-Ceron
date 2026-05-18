# Taller Evaluativo – Informática 2: Unidad 3
# Introducción a la Informática Médica

Janna Valentina Castañeda - 1.031.652.174
Fernando Enrique Jaramillo - 1.080.048.748

# 1. Descripción del proyecto

Aplicación en Python que automatiza la lectura y procesamiento de archivos DICOM, extrae metadatos clínicos relevantes, calcula estadísticas básicas de imagen con NumPy y aplica tecnicas de preprocesamiento con OpenCV (ecualización de histograma y detección de bordes Canny). Los resultados se consolidan en un DataFrame de Pandas y se exportan en CSV junto con las imágenes procesadas

**Explicación sencilla de cómo funciona el código**

El código está diseñado para trabajar automáticamente con imágenes médicas en formato DICOM. Su funcionamiento se basa en una serie de pasos organizados:

1. Primero busca los archivos DICOM dentro de una carpeta
2. Luego lee cada archivo usando pydicom
3. Extrae información importante del paciente y del estudio
4. Convierte la imagen en una matriz numérica para poder analizarla
5. Calcula estadísticas básicas como la intensidad promedio
6. Mejora el contraste de la imagen mediante ecualización
7. Detecta bordes usando el algoritmo de Canny
8. Guarda tanto las imágenes procesadas como los datos obtenidos

Todo esto se realiza automáticamente gracias a la clase ProcesadorDICOM, que centraliza toda la lógica del programa.

**Estructura del proyecto**

    procesador_dicom.py : Clase ProcesadorDICOM (lógica principal)
    main.py             : Punto de entrada
    dicom_files/        : Directorio con archivos .dcm de entrada
    output/             : Imágenes PNG procesadas + CSV de metadatos


# 2. DICOM vs HL7

**DICOM** (Digital Imaging and Communications in Medicine) es el estándar global para el almacenamiento, transmisión e interpretación de imágenes médicas (radiografías, tomografías, resonancias, etc.). Cada archivo encapsula tanto la imagen como los metadatos clínicos del paciente y del estudio en un único objeto, garantizando que cualquier sistema compatible (PACS, estaciones de diagnóstico) pueda leerlo correctamente

**HL7** (Health Level 7) es un estándar para el intercambio de información clínica no-imagen: órdenes médicas, resultados de laboratorio, admisiones de pacientes, notas clínicas, etc. Su versión moderna, **FHIR** (Fast Healthcare Interoperability Resources), expone los datos como recursos REST-JSON/XML consumibles por aplicaciones web

En la práctica los dos estándares son complementarios: HL7 gestiona la orden de un estudio y HL7 recibe el informe radiológico, mientras DICOM transporta las imágenes entre los equipos de adquisición y los sistemas de visualización


# 3. Ecualización de histograma y Canny en imágenes médicas

1. Ecualización de histograma (`cv2.equalizeHist`)

Redistribuye los niveles de intensidad de la imagen para mejorar el contraste global, útil cuando la imagen tiene píxeles concentrados en un rango estrecho (muy oscura o muy clara)

    # Ventajas: Mejora la visualización de estructuras con bajo contraste (nódulos pulmonares, calcificaciones). Sencilla de implementar y computacionalmente barata. Sirve como paso previo a algoritmos de segmentación
    # Limitaciones: Puede saturar regiones de alta intensidad y enmascarar diferencias sutiles de tejido. En mamografías o imágenes de alta resolución puede introducir artefactos. No es adaptativa: aplica la misma transformación a toda la imagen
    # Cuándo es útil?: Preprocesamiento rápido para detección de estructuras grandes (radiografías de tórax, huesos)
    # Cuándo es perjudicial?: Diagnóstico de lesiones pequeñas donde el contraste local es clínicamente significativo (p.ej. ROI cerebral en RM). Se prefiere *CLAHE* (ecualización adaptativa) en ese caso.

2. Detección de bordes con Canny (`cv2.Canny`)

Aplica un detector multietapa (suavizado gaussiano → gradiente → supresión de no-máximos → histéresis con dos umbrales) para resaltar contornos.

Umbrales elegidos: `th1 = 50`, `th2 = 150` (relación 1:3 recomendada por Canny). El umbral bajo captura bordes débiles conectados a bordes fuertes, mientras el alto descarta ruido

    # Ventajas: Resalta contornos anatómicos (silueta cardíaca, bordes óseos, contorno pulmonar). Útil como entrada a algoritmos de segmentación automática
    # Limitaciones: Muy sensible al ruido; imágenes DICOM de 12-16 bits normalizadas a 8 bits pierden información. La elección de umbrales no es universal y varía por modalidad. Puede fragmentar bordes continuos
    # Escenarios útiles: Detección del contorno de órganos, segmentación de huesos en radiografías, preprocesamiento para redes neuronales.
    # Escenarios perjudiciales: Imágenes con mucho ruido de cuantización (imagen normalizada pierde gradaciones). En diagnóstico directo, un borde falso o ausente puede inducir errores clínicos


# 4. Dificultades encontradas e importancia de Python

1. Dificultades

- Tags ausentes: Muchos archivos DICOM de prueba están anonimizados; campos como `PatientName` o `StudyDescription` no están presentes. Se resolvió con `getattr(ds, tag, None)` y marcando el valor como `"N/A"`
- Archivos sin píxeles: Modalidades SR (Structured Report) y PR (Presentation State) no contienen `pixel_array`. Se manejó con `try/except` en el bloque de procesamiento de imagen
- Profundidad de bits variable: las imágenes DICOM pueden ser de 12 o 16 bits; OpenCV espera `uint8`, por lo que la normalización al rango [0, 255] es obligatoria antes de cualquier operación
- Arrays 3D: Algunas imágenes multiframe o en color tienen `ndim == 3`; se tomó el primer canal para garantizar compatibilidad con `equalizeHist`

2. Importancia de las herramientas Python

El ecosistema científico de Python (**pydicom, NumPy, Pandas, OpenCV**) permite construir en pocas líneas de código un flujo completo de ingesta, análisis y procesamiento de imágenes médicas que en otros lenguajes requeriría frameworks mucho más complejos. La interoperabilidad entre estas librerías (todas operan sobre arrays NumPy) facilita la integración y reduce la curva de aprendizaje, lo que resulta clave en entornos clínicos donde la validación y el mantenimiento del software son críticos.
