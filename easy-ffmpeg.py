import argparse
import os
import subprocess
import sys
from typing import List, Optional


def generate_output_filename(input_filename: str, output_filename: Optional[str]) -> str:
    if output_filename:
        return output_filename
    else:
        base_name, extension = os.path.splitext(input_filename)
        return f"{base_name}-out{extension}"


def calculate_bufsize(bitrate: int) -> str:
    bufsize = int(bitrate) * 2
    return f"{bufsize}k"


def main() -> None:
    parser = argparse.ArgumentParser(description="Do stuff with ffmpeg using using the GPU (Nvidia)")
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-r", "--resolution", choices=["240p", "360p", "480p", "540p", "720p", "1080p", "1440p", "4K"], help="Output resolution")
    parser.add_argument("-b", "--bitrate", type=int, help="Video bitrate (in kbps)")
    parser.add_argument("-ab", "--audio-bitrate", type=int, help="Audio bitrate (in kbps)")
    parser.add_argument("--other", nargs="*", help="Additional ffmpeg options")

    common_video_bitrates = ["200k", "500k", "1000k", "1500k", "2000k"]
    common_audio_bitrates = ["64k", "96k", "128k", "192k", "256k"]

    if len(sys.argv) == 1:
        parser.print_help()
        print(f"\nCommon video bitrates: {', '.join(common_video_bitrates)}")
        print(f"Common audio bitrates: {', '.join(common_audio_bitrates)}")
        sys.exit(1)

    args = parser.parse_args()

    cmd: List[str] = ["ffmpeg", "-hwaccel_device", "0", "-hwaccel", "cuda", "-i", args.input]

    if args.resolution:
        resolutions = {
            "240p": "426:240",
            "360p": "640:360",
            "480p": "854:480",
            "540p": "960:540",
            "720p": "1280:720",
            "1080p": "1920:1080",
            "1440p": "2560:1440",
            "4K": "3840:2160"
        }
        cmd.extend(["-vf", f"scale={resolutions[args.resolution]}"])

    if args.bitrate:
        cmd.extend(["-b:v", f"{args.bitrate}k", "-maxrate", f"{args.bitrate}k", "-bufsize", calculate_bufsize(args.bitrate)])

    if args.audio_bitrate:
        cmd.extend(["-c:a", "aac", "-b:a", f"{args.audio_bitrate}k"])

    if not (args.other is None):
        cmd.extend(args.other)  # other opts after --other *

    output_filename = generate_output_filename(args.input, args.output)
    cmd.extend(["-c:v", "h264_nvenc", "-preset", "slow", "-c:a", "copy", output_filename])

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
