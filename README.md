# pypredict
Real-time stock market predictions using an event-driven architecture

## Steps to run the application

Create a virtual environment

```
$ virtualenv venv
```

Activate the virtual environment

```
$ source venv/bin/activate
```

Install the required packages

```
$ pip install -r pypredict/requirements.txt
```

Run the publisher
```
$ python pypredict/trades.py publish
```

Run the subscriber
```
$ python pypredict/trades.py subscribe
```

Run the application

```
$ uvicorn pypredict.main:app --reload
```

Note: the `reload` flag provides the ability to refresh the application after code changes.  It is not necessary.

## Containerizing the application

Run docker container

```
$ docker-compose up
```

Go to http://localhost to view the application