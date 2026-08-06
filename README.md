# Docker Workshop

Notes and references covering containerization, Python virtual environments using `uv`, PostgreSQL databases in Docker, and multi-container orchestration with Docker Compose.

---

## 1. Introduction & Basic Docker Commands

### Basic `docker run` Syntax
Run a container based on a specific image:
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

#### Examples:
```bash
# Run an interactive Ubuntu session and remove the container upon exit
docker run -it --rm ubuntu

# Run Python container in background (detached mode)
docker run -d python:3.9.16-slim

# Run container in background with a custom container name
docker run -dt --name my_python_container python:3.9.16-slim

# Override default entrypoint with bash shell
docker run -it --rm --entrypoint=bash python:3.9.16-slim

# Mount host directory into container (bind mount)
docker run -it --rm -v $(pwd)/test:/app/test --entrypoint=bash python:3.9.16-slim
```

#### Common Flags for `docker run`:
* `-i` (`--interactive`): Keeps STDIN open even if not attached.
* `-t` (`--tty`): Allocates a pseudo-TTY (terminal).
* `--rm`: Automatically removes the container when it exits.
* `--name`: Assigns a custom name to the container.
* `-d` (`--detach`): Runs container in background and prints container ID.
* `--entrypoint`: Overrides the default entrypoint specified in the image Dockerfile.
* `-v` (`--volume`): Mounts a host directory or named volume into the container path.
* `-e` (`--env`): Sets environment variables inside the container.
* `-p` (`--publish`): Maps container port to host port (`HOST_PORT:CONTAINER_PORT`).

---

### Container & Image Management

#### Managing Containers:
```bash
# List running containers
docker ps

# List all containers (running and stopped)
docker ps -a

# List container IDs only
docker ps -q

# Stop a running container gracefully (SIGTERM)
docker stop <CONTAINER_ID_OR_NAME>

# Forcefully stop a container immediately (SIGKILL)
docker kill <CONTAINER_ID_OR_NAME>

# Remove all stopped containers
docker rm $(docker ps -aq)

# Force remove a running container
docker rm -f <CONTAINER_NAME>

# View container logs
docker logs <CONTAINER_NAME>

# Stream logs in real-time
docker logs -f --tail 100 <CONTAINER_NAME>

# Execute an interactive shell inside a running container
docker exec -it <CONTAINER_NAME> bash

# Inspect detailed configuration of a container or image
docker inspect <CONTAINER_NAME_OR_ID>

# Live stream of container resource usage statistics
docker stats

# Copy files between container and local host filesystem
docker cp <HOST_PATH> <CONTAINER_NAME>:<CONTAINER_PATH>
docker cp <CONTAINER_NAME>:<CONTAINER_PATH> <HOST_PATH>
```

#### Managing Images:
```bash
# List local Docker images
docker image ls -a

# Remove a specific image
docker image rm <IMAGE_ID_OR_NAME>

# Delete unused/dangling images
docker image prune

# Clean up stopped containers, unused networks, and dangling images
docker system prune -a --volumes
```

---

## 2. Virtual Environment (`uv`)

Package and virtual environment management in Python using `uv`.

```bash
# Initialize project with a specific Python version
uv init --python=3.13

# Add dependencies and copy packages to local .venv
uv add pandas pyarrow --link-mode=copy

# Add development dependencies
uv add --dev pytest ruff

# Execute script inside virtual environment
uv run python pipeline.py 10

# Sync dependencies with lockfile
uv sync

# Generate/update lockfile
uv lock
```

---

## 3. Dockerizing Pipeline

### Core `Dockerfile` Instructions:
* `FROM`: Sets the base image (multi-stage builds use `--from` to copy build artifacts).
* `ARG`: Defines build-time variables.
* `ENV`: Sets persistent environment variables inside the container.
* `WORKDIR`: Sets working directory for `RUN`, `CMD`, `ENTRYPOINT`, and `COPY`.
* `COPY`: Copies files/folders from host machine into container image.
* `RUN`: Executes shell commands during image build process (creates a new layer).
* `EXPOSE`: Documents which ports the container listens on at runtime.
* `ENTRYPOINT`: Configures container default executable command.
* `CMD`: Provides default arguments for `ENTRYPOINT` or default fallback command.

### Building and Tagging Images:
```bash
# Build image using default Dockerfile in current directory (.)
docker build -t test:pandas .

# Build image using custom Dockerfile name
docker build -f Dockerfile.dev -t pipeline:dev .

# Build without using cached layers
docker build --no-cache -t pipeline:v1 .

# View layer history of an image
docker history <IMAGE_NAME>

# Tag an existing image for remote registry
docker tag pipeline:dev username/pipeline:latest
```

> **Note (`uv` in Docker):** Using `--no-install-project` flag with `uv` installs dependencies without installing the project itself, optimizing layer caching during Docker build.

---

## 4. PostgreSQL in Docker

### Storage Strategy: Named Volumes vs Bind Mounts

| Feature | Named Volume (`volume_name:/path`) | Bind Mount (`/host/path:/container/path`) |
| :--- | :--- | :--- |
| **Management** | Fully managed by Docker daemon inside host system | Directly mapped to host filesystem directory |
| **Portability** | High (isolated from host OS structural changes) | Medium (requires exact path on host) |
| **Best Use Case** | Databases, persistent storage without manual edit | Development code mounting, live code reload |

### Running PostgreSQL Container:
```bash
# Remove volume (optional cleanup)
docker volume rm ny_taxi_postgres_data

# Run PostgreSQL container with persistent volume and exposed port
docker run -d --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5433:5432 \
  --name postgres_db \
  postgres:18
```

### Volume Utility Commands:
```bash
# List all Docker volumes
docker volume ls

# Inspect volume detailed information (driver, mountpoint)
docker volume inspect ny_taxi_postgres_data

# Remove unused volumes
docker volume prune
```

### Connecting to Database via `pgcli`:
```bash
# Add pgcli dev dependency
uv add --dev pgcli

# Connect to database running on host port 5433
uv run pgcli -h localhost -p 5433 -u root -d ny_taxi
```

---

## 5 & 6. Data Ingestion & Jupyter Notebook

ETL pipeline development using Jupyter Notebooks and parameterization for PostgreSQL ingestion.

### Setting up Jupyter Environment:
```bash
# Install Jupyter and IPykernel dependencies
uv add --dev jupyter
uv add ipykernel

# Register virtual environment kernel with Jupyter
uv run python -m ipykernel install --user --name pipeline-venv --display-name "Python (.venv)"

# Launch Jupyter Notebook server
uv run jupyter notebook

# Convert notebook to executable Python script
uv run jupyter nbconvert --to=script notebook.ipynb
mv notebook.py ingest_data.py
```

### Script Parameterization using `click`:
```python
import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5433, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    # Ingest data in chunks into target PostgreSQL database
    print(f"Connecting to {pg_host}:{pg_port}/{pg_db} as {pg_user}...")

if __name__ == '__main__':
    run()
```

---

## 7. PGAdmin Integration & Docker Networks

Custom Docker network allows containers to discover and communicate with each other by container name (DNS lookup).

```bash
# Create user-defined bridge network
docker network create pg-network

# List available networks
docker network ls

# Inspect network configuration and connected containers
docker network inspect pg-network

# Run PostgreSQL container in network
docker run -d \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5433:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18

# Run PGAdmin container in the same network
docker run -d \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

---

## 8. Dockerizing Ingestion Script

Packaging data ingestion logic into an image and executing inside the shared Docker network.

```bash
# Build ingestion image
docker build -f Dockerfile.ingestion -t pipe:ingestion .

# Run container inside 'pg-network' using container hostname 'pgdatabase'
docker run -it --network=pg-network pipe:ingestion \
  --pg-host=pgdatabase \
  --pg-port=5432
```

---

## 9. Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications via a declarative `docker-compose.yml` file.

### Complete `docker-compose.yml` File Structure

```yaml
services:
  pgdatabase:
    image: postgres:18
    container_name: pgdatabase
    restart: always
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - ny_taxi_postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - pg-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U root -d ny_taxi"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: "admin@admin.com"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    ports:
      - "8085:80"
    networks:
      - pg-network
    depends_on:
      pgdatabase:
        condition: service_healthy

volumes:
  ny_taxi_postgres_data:
    driver: local
  pgadmin_data:
    driver: local

networks:
  pg-network:
    driver: bridge
```

---

### Detailed Breakdown of Docker Compose Keys

1. **`services`**: Defines the individual containers that form the application stack.
   * **`image`**: Specifies the Docker Hub image to pull and run.
   * **`build`**: (Alternative to `image`) Path to Dockerfile directory or object specifying `context` and `dockerfile` to build locally.
   * **`container_name`**: Custom name assigned to the container (overrides default `project_service_1` format).
   * **`environment`**: Defines environment variables inside container runtime. Can also reference `.env` files using `env_file: .env`.
   * **`volumes`**: Mounts named volumes or host paths into container filesystem (`HOST_PATH:CONTAINER_PATH`).
   * **`ports`**: Exposes container ports to host machine (`HOST_PORT:CONTAINER_PORT`).
   * **`networks`**: Connects container to custom user-defined networks for DNS resolution.
   * **`restart`**: Defines container restart policy (`no`, `always`, `on-failure`, `unless-stopped`).
   * **`depends_on`**: Expresses dependency order between services. Can wait for health checks before starting dependent services.
   * **`healthcheck`**: Periodically runs command inside container to check if service is healthy and ready to accept connections.

2. **`volumes`**: Top-level section declaring persistent volumes managed by Docker daemon across service updates.

3. **`networks`**: Top-level section declaring custom isolated networks shared among services.

---

### Essential Docker Compose CLI Commands

```bash
# Start all services defined in docker-compose.yml in background (detached)
docker compose up -d

# Build images before starting containers
docker compose up -d --build

# View status of running containers in current stack
docker compose ps

# View live streamed logs for all services
docker compose logs -f

# View live streamed logs for a specific service
docker compose logs -f pgdatabase

# Execute command inside a running service container
docker compose exec pgdatabase bash

# Stop running containers without removing volumes or networks
docker compose stop

# Stop containers, remove containers and networks created by 'up'
docker compose down

# Stop containers and destroy named volumes (WARNING: deletes database data)
docker compose down -v

# Validate and view generated Compose configuration
docker compose config
```