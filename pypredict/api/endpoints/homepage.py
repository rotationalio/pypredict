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

    def __init__(self, websocket, topic="predictions"):
        self.websocket = websocket
        self.topic = topic
        self.ensign = Ensign()

    async def generate_price_info(self, event):
        data = json.loads(event.data)
        price_dict = dict()
        price_dict["symbol"] = data["symbol"]
        price_dict["price_pred"] = data["price_pred"]
        price_dict["price"] = data["price"]
        price_dict["time"] = data["time"]
        await self.websocket.send_json(price_dict)
    
    async def subscribe(self):
        """
        Subscribe to trading events from Ensign and run an
        online model pipeline and publish predictions to a new topic.
        """
        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.topic)
        # Subscribe to the topic.
        # self.generate_price_info is a callback function that gets executed when 
        # a new event arrives in the topic
        await self.ensign.subscribe(topic_id, on_event=self.generate_price_info)
              
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriber = PredictionsSubscriber(websocket)
    await subscriber.subscribe()
    # create a Future and await its result - this will ensure that the
    # subscriber will run forever since nothing in the code is setting the
    # result of the Future
    await asyncio.Future()

@router.get("/")
async def home(request: Request):
	return templates.TemplateResponse("pages/homepage.html",{"request":request})