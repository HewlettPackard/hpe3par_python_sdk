FROM library/python:3

ARG FLASK_PORT=5001

WORKDIR /usr/src

RUN git clone https://github.com/HewlettPackard/hpe3par_python_sdk.git \
    && cd hpe3par_python_sdk \
    && pip install . \
    && pip install flask

EXPOSE $FLASK_PORT

VOLUME [ "/usr/src" ]

CMD [ "python", "hpe3par_python_sdk/test/HPE3ParMockServer_flask.py -port $FLASK_PORT" ]
