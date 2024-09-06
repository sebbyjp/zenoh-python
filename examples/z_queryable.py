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
import json
import time

import zenoh
<<<<<<< HEAD
from zenoh import Sample

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog="z_queryable",
    description="zenoh queryable example")
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
                    default="demo/example/zenoh-python-queryable",
                    type=str,
                    help="The key expression matching queries to reply to.")
parser.add_argument("--value", "-v", dest="value",
                    default="Queryable from Python!",
                    type=str,
                    help="The value to reply to queries.")
parser.add_argument("--complete", dest="complete",
                    default=False,
                    action="store_true",
                    help="Declare the queryable as complete w.r.t. the key expression.")
parser.add_argument("--config", "-c", dest="config",
                    metavar="FILE",
                    type=str,
                    help="A configuration file.")
=======

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog="z_queryable", description="zenoh queryable example"
)
parser.add_argument(
    "--mode",
    "-m",
    dest="mode",
    choices=["peer", "client"],
    type=str,
    help="The zenoh session mode.",
)
parser.add_argument(
    "--connect",
    "-e",
    dest="connect",
    metavar="ENDPOINT",
    action="append",
    type=str,
    help="Endpoints to connect to.",
)
parser.add_argument(
    "--listen",
    "-l",
    dest="listen",
    metavar="ENDPOINT",
    action="append",
    type=str,
    help="Endpoints to listen on.",
)
parser.add_argument(
    "--key",
    "-k",
    dest="key",
    default="demo/example/zenoh-python-queryable",
    type=str,
    help="The key expression matching queries to reply to.",
)
parser.add_argument(
    "--payload",
    "-p",
    dest="payload",
    default="Queryable from Python!",
    type=str,
    help="The payload to reply to queries.",
)
parser.add_argument(
    "--complete",
    dest="complete",
    default=False,
    action="store_true",
    help="Declare the queryable as complete w.r.t. the key expression.",
)
parser.add_argument(
    "--config",
    "-c",
    dest="config",
    metavar="FILE",
    type=str,
    help="A configuration file.",
)
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657

args = parser.parse_args()
conf = (
    zenoh.Config.from_file(args.config) if args.config is not None else zenoh.Config()
)
if args.mode is not None:
    conf.insert_json5("mode", json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5("connect/endpoints", json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5("listen/endpoints", json.dumps(args.listen))
key = args.key
payload = args.payload
complete = args.complete

# Zenoh code  --- --- --- --- --- --- --- --- --- --- ---


<<<<<<< HEAD
def queryable_callback(query) -> None:
    print(f">> [Queryable ] Received Query '{query.selector}'" + (f" with value: {query.value.payload}" if query.value is not None else ""))
    query.reply(Sample(key, value))
=======
def queryable_callback(query):
    print(
        f">> [Queryable ] Received Query '{query.selector}'"
        + (
            f" with payload: {query.payload.deserialize(str)}"
            if query.payload is not None
            else ""
        )
    )
    query.reply(key, payload)
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657


def main() -> None:
    # initiate logging
    zenoh.try_init_log_from_env()

    print("Opening session...")
<<<<<<< HEAD
    session = zenoh.open(conf)

    print(f"Declaring Queryable on '{key}'...")
    queryable = session.declare_queryable(key, queryable_callback, complete)
=======
    with zenoh.open(conf) as session:
        print("Declaring Queryable on '{}'...".format(key))
        session.declare_queryable(key, queryable_callback, complete=complete)
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657

        print("Press CTRL-C to quit...")
        while True:
            try:
                time.sleep(1)
            except Exception as err:
                print(err, flush=True)
                raise


if __name__ == "__main__":
    main()
