FROM python:3.12-slim

# Don't run as root
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py .

EXPOSE 8080

CMD ["python", "app.py"]
