# pypredict
Real-time stock market predictions using an event-driven architecture

## Steps to run the application

### Create a virtual environment

```
$ virtualenv venv
```

### Activate the virtual environment

```
$ source venv/bin/activate
```

### Install the required packages

```
$ pip install -r requirements.txt
```

### Open three terminal windows

#### Run the publisher in the first window (make sure to activate the virtual environment first)
```
$ source venv/bin/activate
```

```
$ python pypredict/trades.py publish
```

#### Run the subscriber in the second window (make sure to activate the virtual environment first)
```
$ source venv/bin/activate
```
```
$ python pypredict/trades.py subscribe
```

#### Run the website in the third window (make sure to activate the virtual environment first)
```
$ source venv/bin/activate
```
```
$ uvicorn pypredict.main:app --reload
```

Note: the `reload` flag provides the ability to refresh the application after code changes.  It is not necessary.

## Containerizing the application

Run docker container

```
$ docker-compose up
```

Go to http://localhost:8000 to view the application