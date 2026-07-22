# 1. Base Python official image use kar rahe hain
FROM python:3.11-slim

# 2. Python memory buffering aur cache block settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Container ke andar workspace directory set kar rahe hain
WORKDIR /app

# 4. Frontend dependencies pehle install karenge optimization ke liye
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Poora frontend application source code container mein copy kar rahe hain
COPY . .

# 6. Streamlit jis standard port par chalta hai use expose kar rahe hain
EXPOSE 8501

# 7. Streamlit service ko network address 0.0.0.0 par bind karke chalane ki command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]