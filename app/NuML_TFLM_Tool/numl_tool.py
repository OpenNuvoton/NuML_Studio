"""NuML_TFLM_Tool command line interface."""
import time
import argparse
import sys

from .project_generate import add_generate_parser
t2 = time.time()
from .project_build import add_build_parser
t3 = time.time()
from .project_flash import add_flash_parser
t4 = time.time()
from .project_deploy import add_deploy_parser
t5 = time.time()
from .project_ei_generate import add_ei_generate_parser
t6 = time.time()

print("INFO: Imports numl_tool times:", t3-t2, t4-t3, t5-t4, t6-t5)

REGISTERED_PARSER = [add_generate_parser, add_build_parser, add_flash_parser, add_deploy_parser, add_ei_generate_parser]

def register_parser(make_subparser):
    """
    Utility function to register a subparser for TFLM.

    Functions decorated with `NuML_TFLM_TOOL.project_xxx.add_xxx_parser` will be invoked
    with a parameter containing the subparser instance they need to add itself to,
    as a parser.

    Example
    -------

        def add_xxx_parser(main_subparser):
            subparser = main_subparser.add_parser('example', help='...')
            ...

    """
    print(make_subparser)
    REGISTERED_PARSER.append(make_subparser)
    return make_subparser


def _main(argv):
    """NuML_TFLM_Tool command line interface."""

    parser = argparse.ArgumentParser(
        prog="numl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="nuvoton ml toolkit",
        epilog=__doc__,
        # Help action will be added later, after all subparsers are created,
        # so it doesn't interfere with the creation of the dynamic subparsers.
        add_help=False,
    )

    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase verbosity")
    parser.add_argument("--version", action="store_true", help="print the version and exit")

    subparser = parser.add_subparsers(title="commands")
    for make_subparser in REGISTERED_PARSER:
        make_subparser(subparser, parser)

    # Finally, add help for the main parser.
    parser.add_argument("-h", "--help", action="help", help="show this help message and exit.")

    args = parser.parse_args(argv)
    if args.verbose > 3:
        args.verbose = 3

    if args.version:
        sys.stdout.write("v.0.01 \n")
        return 0
    if not hasattr(args, "func"):
        # In case no valid subcommand is provided, show usage and exit
        parser.print_help(sys.stderr)
        return 1

    try:
        return args.func(args)
    except Exception:
        sys.stderr.write(traceback.format_exc())
        return 1


def main(argv=None):
    if argv is None:
        _main(sys.argv[1:])
    else:
        _main(argv)

# if __name__ == "__main__":
# for Pystand
def start(argv=None):
    main(argv)
