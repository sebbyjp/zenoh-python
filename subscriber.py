import time
from pydub import AudioSegment
from pydub.playback import play
import zenoh

def subscriber(session, key):
    print(f"Subscribing to '{key}'...")
    sub = session.declare_subscriber(key, lambda sample: play(AudioSegment(data=sample.payload, sample_width=2, frame_rate=44100, channels=2)))
    print("Press CTRL-C to quit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    sub.undeclare()
