import os
import sys
import json
import asyncio
from datetime import datetime

import websockets
from pyensign.events import Event
from pyensign.ensign import Ensign

class TradesPublisher:
    """
    TradesPublisher queries an API for trading updates and publishes events to Ensign.
    """

    def __init__(self, symbols=["AAPL"], topic="trades"):
        self.symbols = symbols
        self.topic = topic
        self.ensign = Ensign()

    def run(self):
        """
        Run the publisher forever.
        """

        # Load finnhub API key from environment variable.
        token = os.environ.get("FINNHUB_API_KEY")
        if token is None:
            raise ValueError("FINNHUB_API_KEY environment variable not set.")

        # Run the publisher.
        asyncio.get_event_loop().run_until_complete(self.recv_and_publish(f"wss://ws.finnhub.io?token={token}"))

    async def recv_and_publish(self, uri):
        """
        Receive messages from the websocket and publish events to Ensign.
        """

        # Ensure that the Ensign topic exists before publishing.
        if not await self.ensign.topic_exists(self.topic):
            await self.ensign.create_topic(self.topic)

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    for symbol in self.symbols:
                        await websocket.send(f'{{"type":"subscribe","symbol":"{symbol}"}}')

                    while True:
                        message = await websocket.recv()
                        for event in self.message_to_events(json.loads(message)):
                            await self.ensign.publish(self.topic, event, ack_callback=self.handle_ack, nack_callback=self.handle_nack)
            except websockets.exceptions.ConnectionClosedError as e:
                # TODO: Make sure reconnect is happening for dropped connections.
                print(f"Websocket connection closed: {e}")
                await asyncio.sleep(1)

    async def handle_ack(self, ack):
        ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def handle_nack(self, nack):
        print(f"Could not commit event {nack.id} with error {nack.code}: {nack.error}")

    def message_to_events(self, message):
        """
        Convert a message from the Finnhub API to multiple Ensign events.
        """

        message_type = message["type"]
        if message_type == "ping":
            return
        elif message_type == "trade":
            for trade in message["data"]:
                data = {
                    "price": trade["p"],
                    "symbol": trade["s"],
                    "timestamp": trade["t"],
                    "volume": trade["v"]
                }
                yield Event(json.dumps(data).encode("utf-8"), mimetype="application/json")
        else:
            raise ValueError(f"Unknown message type: {message_type}")

class TradesSubscriber:
    """
    TradesSubscriber subscribes to trading events from Ensign.
    """

    def __init__(self, topic="trades"):
        self.topic = topic
        self.ensign = Ensign()
    
    def run(self):
        """
        Run the subscriber forever.
        """

        asyncio.get_event_loop().run_until_complete(self.subscribe())

    async def subscribe(self):
        """
        Subscribe to trading events from Ensign.
        """

        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.topic)

        # Subscribe to the topic.
        # TODO: Handle dropped stream, but the SDK should really handle this.
        async for event in self.ensign.subscribe(topic_id):
            print(event)

if __name__ == "__main__":
    # Run the publisher or subscriber depending on the command line arguments.
    if len(sys.argv) > 1:
        if sys.argv[1] == "publish":
            publisher = TradesPublisher()
            publisher.run()
        elif sys.argv[1] == "subscribe":
            subscriber = TradesSubscriber()
            subscriber.run()
    print("Usage: python trades.py [publish|subscribe]")