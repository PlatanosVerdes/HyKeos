FROM arm32v7/python:3.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./hykeos.py" ]