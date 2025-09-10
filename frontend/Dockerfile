FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .

# Build the frontend
RUN npm run build

# Use a lightweight web server for static files
RUN npm install -g serve

RUN echo "VITE_API_BASE_URL: $VITE_API_BASE_URL"

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
