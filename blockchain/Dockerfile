FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libssl-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN npm init -y

COPY env_entrupoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/env_entrupoint.sh

ENTRYPOINT ["env_entrupoint.sh"]

COPY . .

RUN python3 -m solcx.install v0.8.0

EXPOSE 2000

CMD ["python", "app.py"]
