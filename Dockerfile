FROM python:3.12-slim

WORKDIR /app

# psycopg[binary] evita precisar de libpq-dev/gcc na imagem — mantém a
# imagem pequena, alinhado ao espírito minimalista do projeto.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
