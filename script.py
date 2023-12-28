# Importar las bibliotecas necesarias
import hashlib
import re
import logging
import tqdm

# Definir los nombres de los archivos de entrada y salida
archivo1 = "archivo1.txt" # Puedes cambiar el nombre y la extensión según el tipo de archivo
archivo2 = "archivo2.txt" # Puedes cambiar el nombre y la extensión según el tipo de archivo
archivo_salida = "bueno.txt" # Puedes cambiar el nombre y la extensión según el tipo de archivo
archivo_errores = "erro.txt" # Puedes cambiar el nombre y la extensión según el tipo de archivo

# Crear un objeto de registro para guardar el resumen de operaciones y errores
logging.basicConfig(filename=archivo_errores, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Crear una función para calcular el hash sha256 de una cadena
def calcular_hash(cadena):
    try:
        # Codificar la cadena en bytes
        cadena_bytes = cadena.encode("utf-8")
        # Crear un objeto hash
        hash_obj = hashlib.sha256()
        # Actualizar el objeto hash con los bytes de la cadena
        hash_obj.update(cadena_bytes)
        # Obtener el hash en formato hexadecimal
        hash_hex = hash_obj.hexdigest()
        # Devolver el hash
        return hash_hex
    except Exception as e:
        # Manejar posibles excepciones y registrarlas
        logging.error(f"Error al calcular el hash de {cadena}: {e}")
        return None

# Crear una función para determinar el tipo de archivo basado en su extensión
def determinar_tipo(archivo):
    # Obtener la extensión del archivo
    extension = archivo.split(".")[-1]
    # Comparar la extensión con los tipos posibles
    if extension == "lst":
        tipo = "lista"
    elif extension == "txt":
        tipo = "texto"
    elif extension == "log":
        tipo = "registro"
    elif extension == "tsv":
        tipo = "valores separados por tabulaciones"
    else:
        tipo = "desconocido"
    # Devolver el tipo
    return tipo

# Crear una función para procesar una línea según el tipo de archivo
def procesar_linea(linea, tipo):
    # Eliminar espacios en blanco al principio y al final de la línea
    linea = linea.strip()
    # Si el tipo es texto, considerar cada línea como una palabra
    if tipo == "texto":
        palabra = linea
    # Si el tipo es lista, separar la línea por comas y obtener la primera palabra
    elif tipo == "lista":
        palabra = linea.split(",")[0]
    # Si el tipo es registro, separar la línea por espacios y obtener la última palabra
    elif tipo == "registro":
        palabra = linea.split()[-1]
    # Si el tipo es valores separados por tabulaciones, separar la línea por tabulaciones y obtener la segunda palabra
    elif tipo == "valores separados por tabulaciones":
        palabra = linea.split("\t")[1]
    # Si el tipo es desconocido, devolver la línea sin procesar
    else:
        palabra = linea
    # Devolver la palabra
    return palabra

# Crear un diccionario para guardar las palabras y los hashes del archivo1
diccionario = {}

# Abrir el archivo1 con una estructura de gestión de contexto
with open(archivo1, "r") as file1:
    # Determinar el tipo de archivo1
    tipo1 = determinar_tipo(archivo1)
    # Registrar el tipo de archivo1
    logging.info(f"El tipo de archivo1 es {tipo1}")
    # Leer cada línea del archivo1
    for line in file1:
        # Procesar la línea según el tipo de archivo1
        palabra = procesar_linea(line, tipo1)
        # Calcular el hash de la palabra
        hash = calcular_hash(palabra)
        # Si el hash es válido, guardar la palabra y el hash en el diccionario
        if hash:
            diccionario[palabra] = hash
        # Si el hash no es válido, registrar el error
        else:
            logging.error(f"No se pudo obtener el hash de {palabra}")

# Crear una lista para guardar las colisiones encontradas
colisiones = []

# Abrir el archivo2 con una estructura de gestión de contexto
with open(archivo2, "r") as file2:
    # Determinar el tipo de archivo2
    tipo2 = determinar_tipo(archivo2)
    # Registrar el tipo de archivo2
    logging.info(f"El tipo de archivo2 es {tipo2}")
    # Crear un objeto de barra de progreso
    barra = tqdm.tqdm(file2)
    # Leer cada línea del archivo2
    for line in barra:
        # Procesar la línea según el tipo de archivo2
        palabra = procesar_linea(line, tipo2)
        # Calcular el hash de la palabra
        hash = calcular_hash(palabra)
        # Si el hash es válido, buscarlo en el diccionario
        if hash:
            # Si el hash está en el diccionario, significa que hay una colisión
            if hash in diccionario.values():
                # Obtener la palabra del archivo1 que tiene el mismo hash
                palabra1 = list(diccionario.keys())[list(diccionario.values()).index(hash)]
                # Guardar la línea del archivo2, la palabra del archivo1 y el hash en la lista de colisiones
                colisiones.append((line, palabra1, hash))
                # Actualizar la barra de progreso con el mensaje de colisión
                barra.set_description(f"Colisión encontrada: {palabra} y {palabra1} tienen el mismo hash {hash}")
            # Si el hash no está en el diccionario, significa que no hay colisión
            else:
                # Actualizar la barra de progreso con el mensaje de no colisión
                barra.set_description(f"No hay colisión: {palabra} tiene el hash {hash}")
        # Si el hash no es válido, registrar el error
        else:
            logging.error(f"No se pudo obtener el hash de {palabra}")

# Abrir el archivo de salida con el modo adecuado para escritura
with open(archivo_salida, "a") as file_salida:
    # Escribir un encabezado con el nombre de los archivos de entrada
    file_salida.write(f"Colisiones entre {archivo1} y {archivo2}\n")
    # Escribir una línea separadora
    file_salida.write("-" * 80 + "\n")
    # Recorrer la lista de colisiones
    for colision in colisiones:
        # Desempaquetar la tupla de colision
        linea, palabra1, hash = colision
        # Escribir la línea del archivo2, la palabra del archivo1 y el hash en el archivo de salida
        file_salida.write(f"Línea del archivo2: {linea}\n")
        file_salida.write(f"Palabra del archivo1: {palabra1}\n")
        file_salida.write(f"Hash sha256: {hash}\n")
        # Escribir una línea separadora
        file_salida.write("-" * 80 + "\n")

# Registrar el número total de colisiones
logging.info(f"Se encontraron {len(colisiones)} colisiones entre {archivo1} y {archivo2}")

# Informar al usuario la finalización del proceso
print(f"El proceso ha terminado. Puedes revisar el archivo de salida {archivo_salida} y el archivo de errores {archivo_errores} para obtener más detalles.")
