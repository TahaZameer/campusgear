FROM python:3.13-slim

WORKDIR /campusgear

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /campusgear/entrypoint.sh

ENTRYPOINT ["/campusgear/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]