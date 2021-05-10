FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN mkdir images
ENTRYPOINT python3 /app/entry.py