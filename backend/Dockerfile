FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /backend

# usa o mesmo ficheiro de requirements do utils/
COPY utils/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copia o código do backend
COPY backend ./backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
