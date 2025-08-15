# En minimal versiyon - hiç apt-get yok
FROM python:3.13-slim

WORKDIR /app

COPY . .

# Direct install - requirements.txt'e gerek yok
RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]