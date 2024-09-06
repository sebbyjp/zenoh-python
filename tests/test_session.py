<<<<<<< HEAD
=======
#
# Copyright (c) 2024 ZettaScale Technology
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
import json
import time
from typing import List, Tuple

import zenoh
from zenoh import CongestionControl, Priority, Query, Sample, Session

import zenoh
from zenoh import CongestionControl, Priority, Query, Sample, Session

SLEEP = 1
MSG_COUNT = 1_000
MSG_SIZE = [1_024, 131_072]


def open_session(endpoints: list[str]) -> tuple[Session, Session]:
    # listen peer
    conf = zenoh.Config()
    conf.insert_json5("listen/endpoints", json.dumps(endpoints))
    conf.insert_json5("scouting/multicast/enabled", "false")
    print("[  ][01a] Opening peer01 session")
    peer01 = zenoh.open(conf)

    # connect peer
    conf = zenoh.Config()
    conf.insert_json5("connect/endpoints", json.dumps(endpoints))
    conf.insert_json5("scouting/multicast/enabled", "false")
    print("[  ][02a] Opening peer02 session")
    peer02 = zenoh.open(conf)

    return (peer01, peer02)


<<<<<<< HEAD
def close_session(peer01: Session, peer02: Session) -> None:
=======
def close_session(peer01: Session, peer02: Session):
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
    print("[  ][01e] Closing peer01 session")
    peer01.close()
    print("[  ][02e] Closing peer02 session")
    peer02.close()


def run_session_qryrep(peer01: Session, peer02: Session) -> None:
    keyexpr = "test/session"

    for size in MSG_SIZE:
        num_requests = 0
        num_replies = 0
        num_errors = 0

        def queryable_callback(query: Query) -> None:
            nonlocal num_requests
            query.reply(keyexpr, bytes(size))
            num_requests += 1

        print("[QR][01c] Queryable on peer01 session")
        queryable = peer01.declare_queryable(
            keyexpr, queryable_callback, complete=False
        )

        time.sleep(SLEEP)

        print(f"[QR][02c] Getting on peer02 session. {MSG_COUNT} msgs.")
        for _ in range(MSG_COUNT):
            replies = peer02.get(keyexpr)
            for reply in replies:
                try:
                    unwraped_reply = reply.ok
                except:
                    unwraped_reply = None

                if unwraped_reply:
                    assert len(unwraped_reply.payload) == size
                    num_replies += 1
                else:
                    num_errors += 1

        time.sleep(SLEEP)
        print(f"[QR][02c] Got on peer02 session. {num_replies}/{MSG_COUNT} msgs.")
        assert num_replies == MSG_COUNT
        assert num_requests == MSG_COUNT
        assert num_errors == 0

        print("[QR][03c] Unqueryable on peer01 session")
        queryable.undeclare()


def run_session_pubsub(peer01: Session, peer02: Session) -> None:
    keyexpr = "test_pub/session"
<<<<<<< HEAD
    msg = b"Pub Message"
=======
    msg = "Pub Message".encode()
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657

    num_received = 0
    num_errors = 0

    def sub_callback(sample: Sample) -> None:
        nonlocal num_received
        nonlocal num_errors
        if (
            sample.key_expr != keyexpr
            or sample.priority != Priority.DATA_HIGH
            or sample.congestion_control != CongestionControl.BLOCK
            or bytes(sample.payload) != msg
        ):
            num_errors += 1
        num_received += 1

    print("[PS][01d] Publisher on peer01 session")
    publisher = peer01.declare_publisher(
        keyexpr, priority=Priority.DATA_HIGH, congestion_control=CongestionControl.BLOCK
    )
    time.sleep(SLEEP)

    print(f"[PS][02d] Subscriber on peer02 session. {MSG_COUNT} msgs.")
    subscriber = peer02.declare_subscriber(keyexpr, sub_callback)
    time.sleep(SLEEP)

<<<<<<< HEAD
    for _ in range(MSG_COUNT):
=======
    for _ in range(0, MSG_COUNT):
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
        publisher.put("Pub Message")

    time.sleep(SLEEP)
    print(f"[PS][02d] Received on peer02 session. {num_received}/{MSG_COUNT} msgs.")
    assert num_received == MSG_COUNT
    assert num_errors == 0

    print("[PS][03d] Undeclare publisher on peer01 session")
<<<<<<< HEAD
    publisher.undeclare()
    print("[PS][04d] Undeclare subscriber on peer02 session")
    subscriber.undeclare()


def run_session_attachment(peer01, peer02) -> None:
    keyexpr = "test_attachment/session"

    last_sample: Sample | None = None

    def callback(sample: Sample) -> None:
        nonlocal last_sample
        last_sample = sample

    print("[A][01d] Publisher on peer01 session")
    publisher = peer01.declare_publisher(keyexpr)
    time.sleep(SLEEP)

    print("[A][02d] Publisher on peer01 session")
    subscriber = peer02.declare_subscriber(keyexpr, callback)
    time.sleep(SLEEP)

    publisher.put("no attachment")
    time.sleep(SLEEP)
    assert last_sample is not None
    assert last_sample.attachment is None

    publisher.put("attachment", attachment={"key1": "value1", b"key2": b"value2"})
    time.sleep(SLEEP)
    attachment = last_sample.attachment
    assert attachment is not None
    assert attachment
    assert len(attachment) == 2
    assert attachment.keys() == list(attachment) == [b"key1", b"key2"]
    assert attachment.values() == [b"value1", b"value2"]
    attachment.update([("key1", b"value1b")], key3="value3")
    assert attachment.items() == [(b"key1", b"value1"), (b"key2", b"value2"), (b"key1", b"value1b"), (b"key3", b"value3")]
    assert attachment.get("foo") is None

    publisher.put("attachment", attachment=[("key", "value")])
    time.sleep(SLEEP)
    assert dict(last_sample.attachment) == {b"key": b"value"}

    print("[A][03d] Undeclare publisher on peer01 session")
    publisher.undeclare()
    print("[A][04d] Undeclare subscriber on peer02 session")
    subscriber.undeclare()


def test_session() -> None:
    zenoh.init_logger()
=======
    publisher.undeclare()
    print("[PS][04d] Undeclare subscriber on peer02 session")
    subscriber.undeclare()


def test_session():
    zenoh.try_init_log_from_env()
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
    (peer01, peer02) = open_session(["tcp/127.0.0.1:17447"])
    run_session_qryrep(peer01, peer02)
    run_session_pubsub(peer01, peer02)
    close_session(peer01, peer02)
