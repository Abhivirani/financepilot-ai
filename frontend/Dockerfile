# FinancePilot AI — Frontend Dockerfile (skeleton)
# No pages/components exist yet; this builds the environment only.

FROM node:20-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "start"]
