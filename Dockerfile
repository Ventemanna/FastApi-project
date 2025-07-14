FROM python:3.13

COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry env use python3
RUN poetry env activate
RUN poetry install --no-root

COPY . .

CMD ["chmod", "+x", "init_db.sh"]
CMD ["./init_db.sh"]
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]