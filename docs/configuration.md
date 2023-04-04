# Configuration

TODO

parser.add_argument(
    "-u", "--user", dest="user", help="Relative path to user-defined functions"
)
parser.add_argument("-f", "--file", dest="file", help="Relative path to script file")
parser.add_argument("-s", "--source", dest="source", help="Relative source directory")
parser.add_argument("-d", "--data", dest="data", help="Relative data directory")
parser.add_argument("-o", "--output", dest="output", help="Relative output directory")
parser.add_argument("-l", "--log", dest="logfile", help="Path to log file")
parser.add_argument("-a", "--scriptargs", type=str)
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
)