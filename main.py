#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pytube import YouTube
import json
from argparse import ArgumentParser
from tqdm import tqdm
import time

class Asignatura():
    """
    Asignatura class
    """
    def __init__(self, nombre: str, lecciones: list, creditos: int, horas: int, profesor: str):
        self.nombre = nombre
        self.creditos = creditos
        self.horas = horas
        self.lecciones = lecciones

    def __repr__(self) -> str:
        return str(f"Asignatura: {self.nombre}")

class Leccion():
    """
    Leccion class
    """
    def __init__(self, nombre: str, url: str, leccion: int):
        self.nombre = nombre
        self.url = url
        self.leccion = leccion

    def __repr__(self) -> str:
        return str(f"Leccion: {self.nombre}")

    

def yt_download(folder: str, video: str):
    """
    Download a video from youtube

    :param folder: Output folder
    :type folder: str
    :param video: Video url
    :type video: str
    :return: Title of the video
    :rtype: str
    """
    yt = YouTube(video)
    stream = yt.streams.get_highest_resolution()# Get max resolution

    while True:
        try:
            stream.download(output_path=f"{folder}/")
        except Exception as err:
            print(err)
            time.sleep(5)
            continue
        break
    return yt.title

def arguments() -> ArgumentParser:
    """
    Parse arguments

    :return: Parsed arguments
    :rtype: ArgumentParser
    """
    parser = ArgumentParser(description="Download videos from youtube")
    parser.add_argument("-f", "--file", help="Json file with list of videos", required=True)
    parser.add_argument("-o", "--output", help="Output folder", required=True)
    args = parser.parse_args()
    return args

def parse_json(file: str) -> list[Asignatura]:
    """
    Parse json file and return a list of Asignatura

    :param file: Json file
    :type file: str
    :return: list of Asignatura
    :rtype: list[Asignatura]
    """
    with open(file, "r", encoding="utf-8") as f:
        asignaturas = json.load(f)
    f.close()
    res = []
    for asignatura in asignaturas:
        lecciones = []
        for leccion in asignatura["lecciones"]:
            lecciones.append(Leccion(leccion["nombre"], leccion["url"], leccion["leccion"]))

        res.append(Asignatura(asignatura["nombre"], lecciones, asignatura["creditos"], asignatura["horas"], asignatura["profesor"]))

    return res

def main(master: list[Asignatura], output: str):
    """
    Main function

    :param master: list of Asignatura
    :type master: list[Asignatura]
    :param output: Output folder
    :type output: str
    """
    # Special Chars on title
    special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", ",", ".", ";", "!", "'", "`", "¡"]
    # Validate directories
    if not os.path.exists(output):
        os.mkdir(output)
    # Begin Download
    for asignatura in tqdm(master, desc="Downloading", unit="asignaturas"):
        os.mkdir(f"{output}/{asignatura.nombre}")
        for leccion in tqdm(asignatura.lecciones, desc="Downloading", unit="lecciones"):
            title = yt_download(f"{output}/{asignatura.nombre}", leccion.url)
            # Remove special characters from title
            for char in special_chars:
                title = title.replace(char, "")
            out_name = f"M1 Lección{leccion.leccion} {asignatura.nombre} - {leccion.nombre}"
            if asignatura.nombre == "Complementarios":
                out_name = f"{leccion.nombre}"
            output_path = f"{output}/{asignatura.nombre}/{out_name}.mp4"
            if not os.path.exists(output_path):
                # Rename file
                os.rename(f"{output}/{asignatura.nombre}/{title}.mp4", output_path)

if __name__ == "__main__":
    """
    Launch script
    """
    args = arguments()
    master = parse_json(args.file)
    output = args.output
    main(master, output)