import os
import json
import asyncio

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
        Run the publisher until the websocket is closed or an error occurs.
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

        async with websockets.connect(uri) as websocket:
            for symbol in self.symbols:
                await websocket.send(f'{{"type":"subscribe","symbol":"{symbol}"}}')

            # TODO: Handle disconnects.

            while True:
                message = await websocket.recv()
                for event in self.message_to_events(json.loads(message)):
                    await self.ensign.publish(self.topic, event, ack_callback=self.ack_callback, nack_callback=self.nack_callback)

    def ack_callback(self, ack):
        print(f"ACK: {ack}")

    def nack_callback(self, nack):
        print(f"NACK: {nack}")

    def message_to_events(self, message):
        """
        Convert a message from the Finnhub API to multiple Ensign events.
        """

        for trade in message["data"]:
            data = {
                "price": trade["p"],
                "symbol": trade["s"],
                "timestamp": trade["t"],
                "volume": trade["v"]
            }
            yield Event(json.dumps(data).encode("utf-8"), mimetype="application/json")
    
if __name__ == "__main__":
    publisher = TradesPublisher()
    publisher.run()