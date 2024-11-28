FROM python:3.12

WORKDIR /tests/functional

COPY requirements.txt .

RUN pip install --no-cache-dir -U pip wheel && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "src"]
