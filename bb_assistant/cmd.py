import argparse
from argparse import ArgumentParser
from bb_assistant.app import v1
from bb_assistant.util.config import Api_Metrics
from streamlit import config as _config
import streamlit.web.bootstrap
# read commandline args to initiate server (runtime starts here !)
def main():
    parser = ArgumentParser(
        prog="BimeBazar Assistant App",
        description="api wrapper for pdf classification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subcommands = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='subcommand',
    )
    run_parser = subcommands.add_parser(
        'run',
        help='Run the rest server',
    )
    run_parser.add_argument(
        '-H', '--host',
        type=str,
        default="0.0.0.0",
        help='host to serve on',
    )
    run_parser.add_argument(
        '-p', '--port',
        type=int,
        default=9000,
        help='Port to listen on',
    )
    run_parser.add_argument(
        '-w', '--num-workers',
        type=int,
        default=1,
        help='Number of workers',
    )
    run_parser.add_argument(
        '-v', '--version',
        type=str,
        default="v1",
        help='Api Version',
    )
    run_parser.add_argument(
        '-a', '--loglevel',
        type=str,
        default="info",
        help='Api logging level',
    )
    args = parser.parse_args()
    if args.subcommand == 'run':
        _config.set_option("server.headless", True)
        _config.set_option("server.address", args.host)
        _config.set_option("browser.serverAddress", args.host)
        _config.set_option("server.port", args.port)
        _config.set_option("browser.serverPort", args.port)
        streamlit.web.bootstrap.run(main_script_path=f"./bb_assistant/app/{args.version}.py",is_hello=False,args=[],flag_options={})
    else:
        parser.print_help()
    return None


if __name__ == "__main__":
    main()


