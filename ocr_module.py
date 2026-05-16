#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ocr_module.py

OCR Text Extraction Module
- Extracts text from images
- Outputs clean text + JSON
- Supports JPG, PNG, HEIC, TIFF
"""

import os
import json
import pytesseract
from PIL import Image

def extract_text(path):
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return {
            "file": path,
            "text": text.strip()
        }
    except Exception as e:
        return {"error": str(e)}

def save_output(data, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 ocr_module.py <image_path>")
        return

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print("File not found:", img_path)
        return

    result = extract_text(img_path)
    out_file = img_path + ".ocr.json"
    save_output(result, out_file)

    print("OCR extracted →", out_file)

if __name__ == "__main__":
    main()
