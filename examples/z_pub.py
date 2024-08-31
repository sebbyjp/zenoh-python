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
import os
import time
from pydub import AudioSegment
from pydub.playback import play
import zenoh

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog="z_pub",
    description="zenoh pub example")
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
                    default="demo/example/zenoh-python-pub",
                    type=str,
                    help="The key expression to publish onto.")
parser.add_argument("--value", "-v", dest="value",
                    default="Pub from Python!",
                    type=str,
                    help="The value to publish.")
parser.add_argument("--iter", dest="iter", type=int,
                    help="How many puts to perform")
parser.add_argument("--audio-file", "-a", dest="audio_file",
                    metavar="FILE",
                    type=str,
                    help="The audio file to stream.",
                    default="/home/ubuntu/seb/audio/faster-whisper-server/faster_whisper_server/out0.wav")
parser.add_argument("--config", "-c", dest="config",
                    metavar="FILE",
                    type=str,
                    help="A configuration file.")

args = parser.parse_args()
conf = zenoh.Config.from_file(args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
audio_file = args.audio_file
key = args.key
value = args.value

def main() -> None:
    # initiate logging
    zenoh.init_logger()

    print("Opening session...")
    session = zenoh.open(conf)

    print(f"Declaring Publisher on '{key}'...")
    pub = session.declare_publisher(key)

    if audio_file is None:
        print("No audio file provided. Exiting...")
        return

    if not os.path.isfile(audio_file):
        print(f"Audio file '{audio_file}' does not exist. Exiting...")
        return

    print(f"Loading audio file '{audio_file}'...")
    audio = AudioSegment.from_file(audio_file)
    chunk_size = 1000  # 1 second chunks

    print("Press CTRL-C to quit...")
    for idx in itertools.count() if args.iter is None else range(args.iter):
        start = idx * chunk_size
        end = start + chunk_size
        if start >= len(audio):
            break
        chunk = audio[start:end]
        buf = chunk.raw_data
        print(f"Putting Audio Data Chunk {idx} ('{key}')... Length: {len(buf)} bytes")
        pub.put(buf)

    pub.undeclare()
    session.close()

main()
