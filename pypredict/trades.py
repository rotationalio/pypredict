import os
import sys
import json
import asyncio
from datetime import datetime

import websockets
from pyensign.events import Event
from pyensign.ensign import Ensign
from river import compose
from river import linear_model
from river import preprocessing


async def handle_ack(ack):
    _ = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)

async def handle_nack(nack):
    print(f"Could not commit event {nack.id} with error {nack.code}: {nack.error}")

class TradesPublisher:
    """
    TradesPublisher queries an API for trading updates and publishes events to Ensign.
    """

    def __init__(self, symbols=["AAPL", "MSFT", "AMZN"], topic="trades"):
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
        topic_id = await self.ensign.topic_id(self.topic)
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    for symbol in self.symbols:
                        await websocket.send(f'{{"type":"subscribe","symbol":"{symbol}"}}')

                    while True:
                        message = await websocket.recv()
                        for event in self.message_to_events(json.loads(message)):
                            await self.ensign.publish(topic_id, event, on_ack=handle_ack, on_nack=handle_nack)
            except websockets.exceptions.ConnectionClosedError as e:
                # TODO: Make sure reconnect is happening for dropped connections.
                print(f"Websocket connection closed: {e}")
                await asyncio.sleep(1)

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
    TradesSubscriber subscribes to trading events from Ensign and runs an
    online model pipeline and publishes predictions to a new topic.
    """

    def __init__(self, sub_topic="trades", pub_topic="predictions"):
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.ensign = Ensign()
        self.model = self.build_model()
    
    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.get_event_loop().run_until_complete(self.subscribe())

    def build_model(self):
        model = compose.Pipeline(
            ('scale', preprocessing.StandardScaler()),
            ('lin_reg', linear_model.LinearRegression())
        )
        return model
    
    def get_timestamp(self, epoch):
        """
        converts unix epoch to datetime
        """
        epoch_time = epoch / 1000.0
        timestamp = datetime.fromtimestamp(epoch_time)
        return timestamp
    
    async def run_model_pipeline(self, event):
        """
        Train an online model and publish predictions to a new topic.
        Run your super smart model pipeline here!
        """
        data = json.loads(event.data)
        # convert unix epoch to datetime
        timestamp = self.get_timestamp(data["timestamp"])
        # extract the microsecond component and use it as a model feature
        x = {"microsecond" : timestamp.microsecond}
        # generate a prediction
        price_pred = round(self.model.predict_one(x), 4)
        price = data["price"]
        # pass the actual trade price to the model
        self.model.learn_one(x, price)

        # create a message that contains the predicted price and the actual price
        message = dict()
        message["symbol"] = data["symbol"]
        message["time"] = timestamp.strftime("%H:%M:%S")
        message["price"] = str(data["price"])
        message["price_pred"] = str(price_pred)

        # create an Ensign event and publish to the predictions topic
        event = Event(json.dumps(message).encode("utf-8"), mimetype="application/json")
        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.pub_topic)
        await self.ensign.publish(topic_id, event, on_ack=handle_ack, on_nack=handle_nack)

    async def subscribe(self):
        """
        Subscribe to trading events from Ensign and run an
        online model pipeline and publish predictions to a new topic.
        """

        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.sub_topic)

        # Subscribe to the topic.
        # self.run_model_pipeline is a callback function that gets executed when 
        # a new event arrives in the topic
        await self.ensign.subscribe(topic_id, on_event=self.run_model_pipeline)
        # create a Future and await its result - this will ensure that the
        # subscriber will run forever since nothing in the code is setting the
        # result of the Future
        await asyncio.Future()

if __name__ == "__main__":
    # Run the publisher or subscriber depending on the command line arguments.
    if len(sys.argv) > 1:
        if sys.argv[1] == "publish":
            publisher = TradesPublisher(symbols=["AAPL", "MSFT", "AMZN"])
            publisher.run()
        elif sys.argv[1] == "subscribe":
            subscriber = TradesSubscriber()
            subscriber.run()
    print("Usage: python trades.py [publish|subscribe]")