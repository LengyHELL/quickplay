from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser


class QuickplayModel:
    def parseArguments(self) -> None:
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
            "-e",
            "--executable",
            dest="executable",
            default="mpv",
            help="MPV executable location.",
            metavar="PATH",
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
            default="_internal/quickplay.txt",
            help="The playlist config text file used for storing playlist elements.",
            metavar="FILE",
        )
        parser.add_argument(
            "-x",
            "--extensions",
            dest="extensions",
            default=".mkv, .mp4",
            help='The extensions to include when searching the directories. \
                (eg.: ".mkv, .mp4, .mov")',
            metavar="LIST",
        )

        return parser.parse_args()
