<br />
<p align="center">
  <a href="https://github.com/Obliie/Valytics">
    <img src="https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt79971d6ef53d8a5f/5e8cdeaa07387e0c9bfff0c5/IMAGE_4.jpg" alt="Header photo" >
  </a>

  <h3 align="center">Valytics</h3>

  <p align="center">
    A VALORANT match analysis app built with React Native, using Python microservices in the backend.
    <br />
    <br />
    <a href="https://twitter.com/Obliie">Contact me</a>
    ·
    <a href="https://github.com/Obliie/Valytics/issues">Issues</a>
    ·
    <a href="https://github.com/Obliie/Valytics/pulls">Pull Requests</a>
  </p>
</p>


# Contents
* [Development](#development)
  * [Prerequisites](#prerequisites)
  * [Setup](#setup)
    * [Frontend](#frontend)
    * [Backend](#backend)
  * [Testing](#testing)
* [Exposed Service Ports](#exposed-service-ports)

# Development

## Prerequisites
* npm
* docker

## Setup
### Frontend
1. Move into the frontend development directory
```sh
cd app-web
```
2. Install NPM packages
```sh
npm install
```
3. Start the Expo Metro bundler
```sh
npm run web
```
### Backend
1. Copy the env.example file and adjust values appropriately
```sh
cp env.example .env
```
2. Start the backend microservice containers
```sh
docker compose --profile backend up
```

## Testing
Run service integration tests:
```sh
docker compose --profile test up
```

Run pre-commit checks:
```sh
docker compose --profile pre-commit up
```

# Exposed Service Ports
Ports for exposed services. This does not include internal services.
| Service                   | Default Port |
| ------------------------- | ------------ |
| Envoy API Gateway         | 8080         |
| Envoy API Gateway Admin   | 21999        |
| Prometheus                | 9090         |