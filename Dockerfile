FROM python:3.11

WORKDIR /code

COPY ./backend/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend /code/

CMD ["fastapi", "run", "main.py", "--port", "80"]
