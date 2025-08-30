import argparse
import os
import glob
import sys
from kickstart import kickstart
from logging import Logger


def main():
    parser = argparse.ArgumentParser(
        prog="legoeye",
        description="Bootstraps and runs the camera framework."
    )
    parser.add_argument(
        "-c", "--config", dest="config",
        help="Path to configuration JSON"
    )
    parser.add_argument(
        "--no-start", dest="start_legoeye",
        action="store_false",
        help="Stops the legoeye from starting",
        default=True
    )
    parser.add_argument(
        "-apr","--add-pre-scripts", dest="pre_script_paths",
        nargs='+', metavar="PATH",
        help=("Add scripts directories or files which will be executed once before picam initialization"
        "the files will be stored in legoeye/scripts/default/pre_picam_init"),
        default=[]
    ) 
    parser.add_argument(
        "-acb","--add-callbacks", dest="callback_script_paths",
        nargs='+', metavar="PATH",
        help=("Add scripts directories or files which will be executed for each frame"
        "the files will be stored in legoeye/scripts/pre_callback"),
        default=[]
    )
    parser.add_argument(
        "-aps","--add-post-scripts", dest="post_script_paths",
        nargs='+', metavar="PATH",
        help=("Add scripts directories or files which will be executed once before picam initialization"
        "the files will be stored in legoeye/scripts/default/pre_picam_init"),
        default=[]
    )
    parser.add_argument(
        "-afps","--add-frame-pro-scripts", dest="frame_pro_script_paths",
        nargs='+', metavar="PATH",
        help=("Add scripts directories or files which will be executed once before picam initialization"
        "the files will be stored in legoeye/scripts/default/pre_picam_init"),
        default=[]
    )

    parser.add_argument(
        "-D", "--set", dest="overrides",
        action="append",
        metavar="KEY=VALUE",
        help=("Define/Override a config setting. Use dot notation for nested keys"
              "e.g. -D streaming.ENABLE=True or --set log.ENABLE=True"),
        default=[]
    )
    args = parser.parse_args()


    if args.pre_script_paths:
        expanded = []
        for pattern in args.pre_script_paths:
            pattern = os.path.expanduser(pattern)

            # use glob to match wildcards (*, ?, [..]) in the pattern if there is any
            matches = glob.glob(pattern)

            if matches:
                # 'matches' is a list of all paths matching the pattern.
                # 'extend' adds each element of 'matches' to 'expanded'.
                expanded.extend(matches)
            else:
                # path doesn't exist, throw warning
                Logger.error(f"Invalid path: {pattern}")
                
        Logger.info(f"Added script paths: {expanded}")

    # Parse overrides into dict
    overrides = {}
    for item in args.overrides:
        if '=' not in item:
            print(f"Invalid override '{item}', use KEY=VALUE format.", file=sys.stderr)
            sys.exit(1)
        key, val = item.split('=', 1)

        # attempt to parse booleans and numbers
        if val.lower() in ('true', 'false'):
            parsed = val.lower() == 'true'
        else:
            try:
                parsed = int(val)
            except ValueError:
                try:
                    parsed = float(val)
                except ValueError:
                    #we interpret the value as normal string here as parsing it as boolean, int and float failed
                    parsed = val
        overrides[key] = parsed
    
    

    if not args.no_start:
        kickstart()

if __name__ == "__main__":
    main()