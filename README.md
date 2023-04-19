<img width="72" height="72" align="right" style="position: absolute;  top: 0; right: 0; padding: 12px;" src="resources/logo.png" alt="Tekst logo"/>

# Tekst <!-- omit in toc -->

Tekst is a collaborative, web-based research platform for displaying, linking, exploring, and enriching resources on natural language texts. It is developed within the scope of the [VedaWeb 2.0](https://vedaweb.uni-koeln.de/) research project on Old Indic texts, where it constitutes the technical basis of the research platform "VedaWeb", which will be launched in its new form as part of the project's efforts.

This is the "main" Tekst repository. While destinct parts of the application code have their own respective repositories (namely the server and client application projects), this very repository is meant as the go-to place for general information, documentation and the resources needed to deploy an instance of the Tekst platform for yourself.

If, however, you want to visit or even contribute to the Tekst code repositories, here's where to look first:

- [**tekst-api**](https://github.com/VedaWebProject/tekst-api) - Codebase of the **Tekst** *server* application.
- [**tekst-web**](https://github.com/VedaWebProject/tekst-web) - Codebase of the **Tekst** *client* application.


## Contents  <!-- omit in toc -->

- [State of development](#state-of-development)
- [Deployment](#deployment)
  - [Docker (recommended)](#docker-recommended)


## State of development

Development on this software is in an early conceptual phase. At this point, there is no usable release or public instance.


## Deployment

### Docker (recommended)
To deploy Tekst with Docker, follow these steps (example commands assume using some kind of loosely POSIX compliant shell):

1. Requirements:
   - [Git](https://git-scm.com/)
   - [Docker](https://docs.docker.com/engine/install), including the [docker-compose-plugin](https://docs.docker.com/compose/install/linux/) (recommended) or [Compose](https://docs.docker.com/compose/install/other/) standalone

2. Clone this repository and change into the resulting directory:

    ```sh
    git clone https://github.com/VedaWebProject/tekst.git
    cd tekst
    ```

3. Copy the `.env.docker` file and name the copy `.env`:

    ```sh
    cp .env.docker .env
    ```

4. Configure the values in `.env` to match your deployment environment and needed features. Use the comments in those files for guidance. If you leave everything unchanged, Tekst will run with sensible defaults for a full-featured, Docker-based production environment served at `/` (root path). By default, the application will later be available via the local port `8087` at `127.0.0.1`.

5. Build the docker images for the **tekst-api** (server) and **tekst-web** (client) applications. **Important:** Whenever you decide to change one of `TEKST_WEB_PATH`, `TEKST_SERVER_URL` or `TEKST_API_PATH` in your `.env` file, you'll have to build the image for **tekst-web** (client) again, as these values are statically replaced in the code during the build process!

    ```sh
    docker compose build tekst-api tekst-web
    ```

    ... now grab a (small) coffee ☕

6. Run the complete application stack with:

    ```sh
    docker compose up
    ```

    Add the `-d` flag to run it in detached mode (in the background).

7. Read [this](https://docs.docker.com/engine/reference/commandline/compose/) to learn how to stop, start, reset (...) the application stack using Docker Compose.
