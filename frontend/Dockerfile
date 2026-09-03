# FinancePilot AI — Frontend Dockerfile (skeleton)
# No pages/components exist yet; this builds the environment only.

FROM node:20-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000

# TODO: switch to `npm run build && npm run start` for production once
# the app has real pages.
CMD ["npm", "run", "dev"]
