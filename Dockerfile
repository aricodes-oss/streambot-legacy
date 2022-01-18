FROM python:3.9

RUN mkdir /code
WORKDIR /code
RUN mkdir streambot

RUN pip install --upgrade pip poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-root

COPY streambot streambot
RUN rm -f streambot/.env

RUN poetry install

CMD ["poetry", "run", "streambot"]
