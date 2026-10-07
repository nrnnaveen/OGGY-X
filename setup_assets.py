#!/usr/bin/env python3
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(BASE_DIR, "static", "videos")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(DEST_DIR, exist_ok=True)

SOURCE_DIR = "/home/naveen/Documents/oggy assests"

if os.path.exists(SOURCE_DIR):
    files = os.listdir(SOURCE_DIR)
    mapping = {
        "Oggy_talking_against_blue_backgr": "idle.mp4",
        "Oggy_listening_attentively": "listening.mp4",
        "Oggy_thinking_and_having_realiza": "thinking.mp4",
        "Oggy_speaking_and_gesturing": "speaking_gesture.mp4",
        "Oggy_talking_to_viewer": "speaking_talk.mp4",
        "Cartoon_character_talking_and_em": "speaking_emote.mp4",
    }
    for src_file in files:
        for pattern, canonical in mapping.items():
            if src_file.startswith(pattern):
                src_path = os.path.join(SOURCE_DIR, src_file)
                dest_path = os.path.join(DEST_DIR, canonical)
                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied {src_file} -> {canonical}")

print("Assets ready.")
