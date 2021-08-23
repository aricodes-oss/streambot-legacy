FROM python:latest

RUN mkdir /code
WORKDIR /code
RUN mkdir streambot

RUN pip install --upgrade poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-root

COPY streambot streambot
RUN rm -f streambot/.env

RUN poetry install

CMD ["poetry", "run", "streambot"]