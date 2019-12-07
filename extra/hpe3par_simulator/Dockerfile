FROM library/python:3

WORKDIR /usr/src

RUN git clone https://github.com/HewlettPackard/hpe3par_python_sdk.git \
    && cd hpe3par_python_sdk \
    && pip install . \
    && pip install flask

EXPOSE 5000

ARG USER=username
ARG PASSWORD=password

VOLUME [ "/usr/src" ]

ENTRYPOINT [ "python" ]

CMD [ "hpe3par_python_sdk/test/HPE3ParMockServer_flask.py", "-debug", "-user", "${USER}", "-password", "${PASS}" ]
