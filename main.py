#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pytube import YouTube
import json
from argparse import ArgumentParser
from tqdm import tqdm
import time

class Asignatura():
    def __init__(self, nombre: str, lecciones: list, creditos: int, horas: int, profesor: str):
        self.nombre = nombre
        self.creditos = creditos
        self.horas = horas
        self.lecciones = lecciones

    def __repr__(self) -> str:
        return str(f"Asignatura: {self.nombre}")

class Leccion():
    def __init__(self, nombre: str, url: str, leccion: int):
        self.nombre = nombre
        self.url = url
        self.leccion = leccion

    def __repr__(self) -> str:
        return str(f"Leccion: {self.nombre}")

    

def yt_download(folder: str, video: str):
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

def arguments():
    parser = ArgumentParser(description="Download videos from youtube")
    parser.add_argument("-f", "--file", help="Json file with list of videos")
    parser.add_argument("-o", "--output", help="Output folder")
    args = parser.parse_args()
    return args

def parse_json(file: str) -> list[Asignatura]:
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
    special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", ",", ".", ";", "!", "'", "`", "¡"]
    if not os.path.exists(output):
        os.mkdir(output)
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
            os.rename(f"{output}/{asignatura.nombre}/{title}.mp4", f"{output}/{asignatura.nombre}/{out_name}.mp4")

if __name__ == "__main__":
    args = arguments()
    master = parse_json(args.file)
    output = args.output
    main(master, output)