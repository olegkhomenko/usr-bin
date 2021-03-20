"""The script trims videos and extracts audio (mode="a")
using specific .txt file with the following structure: FILENAME;STARTFROM;LENGTH
Example:
```
W59CV66z9lQ.mp4;00:04:26;00:00:15
Lb4IcGF5iTQ.mp4;00:16:58;00:00:15
ghfRLCPwMeY.webm;00:00:41;00:00:15
```
"""
import argparse
import platform
import subprocess
from pathlib import Path


def prepare_videos(meta_fpath, mode="v"):
    with open(meta_fpath, "r") as fin:
        videos = fin.readlines()

    for vid in videos:
        if vid.replace(" ", "").startswith("#"):
            continue

        vid = vid.replace("\n", "")
        vid_splitted = vid.split(";")
        if len(vid_splitted) != 3:
            print(f"Skipping for line: {vid_splitted}")
            continue

        fname, start_from, length = vid_splitted
        start_from_suffix = start_from.replace(":", "").replace(".", "")
        length_suffix = length.replace(":", "").replace(".", "")

        ext_idx = -5 if fname.lower().endswith(".webm") else -4

        out_fname = f"{fname[:ext_idx]}_trimmed_{start_from_suffix}_{length_suffix}{fname[ext_idx:]}"

        if mode == "a":
            out_fname = out_fname[:ext_idx] + ".wav"
        elif not out_fname.lower().endswith(".mp4"):  # .avi, .webm, etc. -> .mp4
            out_fname = out_fname[:ext_idx] + ".mp4"

        if Path(out_fname).exists():
            print(f"File already processed: {out_fname}")
            continue

        command = f"ffmpeg -ss {start_from} -t {length} -i '{fname}' '{out_fname}'"

        print(f"Starting for {fname}")
        subprocess.call(command, shell=platform.system() != "Windows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="files.txt", required=True)
    parser.add_argument("--mode", default="v", choices={"v", "a"}, help="Mode, prepare video or audio", required=True)
    args = parser.parse_args()

    prepare_videos(meta_fpath=args.file, mode=args.mode)
