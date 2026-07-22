FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000

# Dev-oriented skeleton: next dev. Switch to `next start` after `next build` for prod-like runs.
CMD ["npm", "run", "dev"]
