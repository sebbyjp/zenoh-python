<<<<<<< HEAD
=======
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

>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
import argparse
import json
import time
<<<<<<< HEAD
import threading
from pydub import AudioSegment
from pydub.playback import play
import zenoh

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog="z_sub",
    description="zenoh sub example")
parser.add_argument("--mode", "-m", dest="mode",
                    choices=["peer", "client", "pub"],
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
                    default="demo/example/zenoh-python-pub",
                    type=str,
                    help="The key expression to subscribe to.")
parser.add_argument("--config", "-c", dest="config",
                    metavar="FILE",
                    type=str,
                    help="A configuration file.")

args = parser.parse_args()
conf = zenoh.Config.from_file(args.config) if args.config is not None else zenoh.Config()
if args.mode is not None and args.mode != "pub":
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
=======

import zenoh

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(prog="z_pub", description="zenoh pub example")
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
    default="demo/example/zenoh-python-pub",
    type=str,
    help="The key expression to publish onto.",
)
parser.add_argument(
    "--payload",
    "-p",
    dest="payload",
    default="Pub from Python!",
    type=str,
    help="The payload to publish.",
)
parser.add_argument("--iter", dest="iter", type=int, help="How many puts to perform")
parser.add_argument(
    "--interval",
    dest="interval",
    type=float,
    default=1.0,
    help="Interval between each put",
)
parser.add_argument(
    "--config",
    "-c",
    dest="config",
    metavar="FILE",
    type=str,
    help="A configuration file.",
)

args = parser.parse_args()
conf = (
    zenoh.Config.from_file(args.config) if args.config is not None else zenoh.Config()
)
if args.mode is not None:
    conf.insert_json5("mode", json.dumps(args.mode))
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
if args.connect is not None:
    conf.insert_json5("connect/endpoints", json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5("listen/endpoints", json.dumps(args.listen))
key = args.key
<<<<<<< HEAD
=======
payload = args.payload

>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657

def main() -> None:
    # initiate logging
    zenoh.try_init_log_from_env()

    print("Opening session...")
    with zenoh.open(conf) as session:

<<<<<<< HEAD
    if args.mode == "pub":
        print(f"Publishing to '{key}'...")
        def publish_loop():
            while True:
                # Here you would add the code to publish data
                time.sleep(1)
        
        publish_thread = threading.Thread(target=publish_loop)
        publish_thread.start()
        
        print("Press CTRL-C to quit...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print(f"Subscribing to '{key}'...")
        sub = session.declare_subscriber(key, lambda sample: play(AudioSegment(data=sample.payload, sample_width=2, frame_rate=44100, channels=2)))
        print("Press CTRL-C to quit...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        sub.undeclare()
    session.close()
=======
        print(f"Declaring Publisher on '{key}'...")
        pub = session.declare_publisher(key)

        print("Press CTRL-C to quit...")
        for idx in itertools.count() if args.iter is None else range(args.iter):
            time.sleep(args.interval)
            buf = f"[{idx:4d}] {payload}"
            print(f"Putting Data ('{key}': '{buf}')...")
            pub.put(buf)

>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657

if __name__ == "__main__":
    main()
