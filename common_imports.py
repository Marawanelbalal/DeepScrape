import sys
import time
import os
import json
import pandas as pd
import matplotlib
import re
from dotenv import load_dotenv
from PyQt6.QtCore import QFile,QIODevice
import io


def read_csv_from_qrc(path, encoding="utf-8"):
    file = QFile(path)
    if not file.open(QIODevice.OpenModeFlag.ReadOnly):
        raise IOError(f"Cannot open resource: {path}")

    byte_data = file.readAll()
    text = bytes(byte_data).decode(encoding)
    return pd.read_csv(io.StringIO(text))