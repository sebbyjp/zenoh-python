#
# Copyright (c) 2022 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#

import argparse
import itertools
import json
import time

import zenoh
from zenoh import Reliability

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog="z_pull",
    description="zenoh pull example")
parser.add_argument("--mode", "-m", dest="mode",
                    choices=["peer", "client"],
                    type=str,
                    help="The zenoh session mode.")
parser.add_argument("--connect", "-e", dest="connect",
                    metavar="ENDPOINT",
                    action="append",
                    type=str,
                    help="Endpoints to connect to.")
parser.add_argument("--listen", "-l", dest="listen",
                    metavar="ENDPOINT",
                    action="append",
                    type=str,
                    help="Endpoints to listen on.")
parser.add_argument("--key", "-k", dest="key",
                    default="demo/example/**",
                    type=str,
                    help="The key expression matching resources to pull.")
parser.add_argument("--config", "-c", dest="config",
                    metavar="FILE",
                    type=str,
                    help="A configuration file.")

args = parser.parse_args()
conf = zenoh.Config.from_file(
    args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
key = args.key

# Zenoh code  --- --- --- --- --- --- --- --- --- --- ---


def listen(sample) -> None:
    print(f">> [Subscriber] Received {sample.kind} ('{sample.key_expr}': '{sample.payload.decode('utf-8')}')")


def main() -> None:
    # initiate logging
    zenoh.init_logger()

    print("Opening session...")
    session = zenoh.open(conf)

    print(f"Declaring Subscriber on '{key}'...")
    sub = session.declare_pull_subscriber(key, listen, reliability=Reliability.RELIABLE())

    print("Press CTRL-C to quit...")
    for idx in itertools.count():
        time.sleep(1)
        print(f"[{idx:4d}] Pulling...")
        sub.pull()

    sub.undeclare()
    session.close()

main()
