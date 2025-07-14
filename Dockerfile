FROM python:3.13

# Сначала копируем только зависимости для кеширования
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry env use python3
RUN poetry env activate
RUN poetry install --no-root
RUN poetry add pytest

# Затем копируем весь код
COPY . .

# Указываем команду запуска (долгоживущий процесс!)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]