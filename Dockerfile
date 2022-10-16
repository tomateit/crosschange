FROM python:3.10

WORKDIR /code

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN /root/.local/bin/poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN /root/.local/bin/poetry install --no-dev

COPY ./ /code/

COPY ./.env /code/.env

CMD ["python", "main.py"]