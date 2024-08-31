import argparse
import json
import time
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
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
key = args.key

def main() -> None:
    # initiate logging
    zenoh.init_logger()

    print("Opening session...")
    session = zenoh.open(conf)

    if args.mode == "pub":
        print(f"Publishing to '{key}'...")
        while True:
            # Here you would add the code to publish data
            time.sleep(1)
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

main()
