FROM python:3.9

RUN mkdir /code
WORKDIR /code
RUN mkdir streambot

RUN pip install --upgrade pip poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-root --no-dev

COPY streambot streambot
RUN rm -f streambot/.env

RUN poetry install --no-dev

CMD ["poetry", "run", "streambot"]
