#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
exif_module.py

EXIF Metadata Extraction Module
- Extracts EXIF metadata from images
- Outputs JSON
- Supports JPG, PNG, HEIC, TIFF
"""

import os
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_exif(path):
    try:
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return {"error": "No EXIF metadata found"}

        exif = {}
        gps = {}

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value

            if tag == "GPSInfo":
                for gps_id in value:
                    gps_tag = GPSTAGS.get(gps_id, gps_id)
                    gps[gps_tag] = value[gps_id]

        return {
            "file": path,
            "exif": exif,
            "gps": gps
        }

    except Exception as e:
        return {"error": str(e)}


def save_json(data, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 exif_module.py <image_path>")
        return

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print("File not found:", img_path)
        return

    result = extract_exif(img_path)
    out_file = img_path + ".exif.json"
    save_json(result, out_file)

    print("EXIF extracted →", out_file)


if __name__ == "__main__":
    main()
