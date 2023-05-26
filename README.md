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

Run the application

```
$ cd pypredict
$ uvicorn main:app --reload
```

Note: the `reload` flag provides the ability to refresh the application after code changes.  It is not necessary.
