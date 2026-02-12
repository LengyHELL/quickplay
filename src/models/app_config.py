import re
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass


@dataclass
class AppConfig:
    folder_file: str
    playlist_file: str
    extensions: list[str]


def parse_arguments() -> AppConfig:
    parser = ArgumentParser(
        add_help=False,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="Show this help message.",
    )
    parser.add_argument(
        "-f",
        "--folder",
        dest="folderFile",
        default="_internal/folders.txt",
        help="The directory config text file used for parsing titles.",
        metavar="FILE",
    )
    parser.add_argument(
        "-p",
        "--playlist",
        dest="playlistFile",
        default="_internal/quickplay.json",
        help="The playlist config text file used for storing playlist elements.",
        metavar="FILE",
    )
    parser.add_argument(
        "-x",
        "--extensions",
        dest="extensions",
        default=".mkv, .mp4",
        help='The extensions to include when searching the directories. (eg.: ".mkv, .mp4, .mov")',
        metavar="LIST",
    )

    args = parser.parse_args()
    extensions = re.sub(r"\s", "", args.extensions).split(",")
    return AppConfig(args.folderFile, args.playlistFile, extensions)
