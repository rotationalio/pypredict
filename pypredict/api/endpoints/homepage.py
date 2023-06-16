import asyncio
import json

from fastapi import APIRouter
from fastapi import Request
from fastapi import WebSocket
from fastapi.templating import Jinja2Templates

from pyensign.ensign import Ensign

from pypredict.core import config

class PredictionsSubscriber:
    """
    PredictionsSubscriber subscribes to a predictions topic from Ensign.
    """

    def __init__(self, topic="predictions"):
        self.topic = topic
        self.ensign = Ensign()

    def run(self):
        """
        Run the subscriber forever.
        """

        asyncio.get_event_loop().run_until_complete(self.subscribe())
    
    async def subscribe(self):
        """
        Subscribe to trading events from Ensign and run an
        online model pipeline and publish predictions to a new topic.
        """

        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.topic)

        # Subscribe to the topic.
        # TODO: Handle dropped stream, but the SDK should really handle this.
        async for event in self.ensign.subscribe(topic_id):
            yield event
              
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriber = PredictionsSubscriber()
    async for event in subscriber.subscribe():
        data = json.loads(event.data)
        price_dict = dict()
        price_dict["symbol"] = data["symbol"]
        price_dict["price_pred"] = data["price_pred"]
        price_dict["price"] = data["price"]
        price_dict["time"] = data["time"]
        await websocket.send_json(price_dict)

@router.get("/")
async def home(request: Request):
	return templates.TemplateResponse("pages/homepage.html",{"request":request})