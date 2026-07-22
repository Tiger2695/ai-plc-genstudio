# 1. Official lightweight Python image use kar rahe hain
FROM python:3.11-slim

# 2. Python standard environment variables set kar rahe hain
# PYTHONDONTWRITEBYTECODE=1 -> .pyc files generation rokta hai
# PYTHONUNBUFFERED=1 -> Logs ko instantly output screen par print karta hai
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Container ke andar ka working directory set kar rahe hain
WORKDIR /app

# 4. Kuch essential system dependencies install kar rahe hain (gcc wagera agar compile ke liye chahiye ho)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 5. Pehle requirements copy karke install karenge (Docker cache optimization ke liye)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Ab poora backend ka source code container ke andar copy karenge
COPY . .

# 7. FastAPI jis port par chalta hai, use container ke andar expose kar rahe hain
EXPOSE 8000

# 8. Uvicorn command jo container start hote hi chalegi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]