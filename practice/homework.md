# Module 1: Docker & Terraform — Practice Workbook

---

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

**My answer:**
```bash
docker run -it --rm --entrypoint=bash python:3.13
pip --version
```
```text
pip 26.1.2 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

---

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

**My answer:**
```text
Correct answers: db:5432 and postgres:5432
```

---

## Question 3. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

**My answer:**
```bash
terraform init, terraform apply -auto-approve, terraform destroy
```

---

## Question 4. Docker Run & Port Mapping (Practical)

Run a PostgreSQL container (`postgres:17-alpine` image) in detached mode.
- Set the environment variable `POSTGRES_PASSWORD` to `secret123`.
- Map port `5432` on the host to port `5432` in the container.
- Name the container `my_test_postgres`.
- Display the logs for this container to confirm the database started successfully.

**My answer:**
```bash
# Paste your commands here:
docker run -itd -p 5432:5432 -e=POSTGRES_PASSWORD=secret123 --rm --name=my_test_postgres  postgres:17-alpine
docker logs my_test_postgres

2026-08-10 09:38:54.245 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-08-10 09:38:54.245 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-08-10 09:38:54.249 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-08-10 09:38:54.256 UTC [55] LOG:  database system was shut down at 2026-08-10 09:38:54 UTC
2026-08-10 09:38:54.262 UTC [1] LOG:  database system is ready to accept connections

```

---

## Question 5. CMD vs ENTRYPOINT (Theoretical)

What is the difference between `CMD` and `ENTRYPOINT` instructions in a `Dockerfile`? What happens when you pass additional arguments at the end of a `docker run` command?

**My answer:**
```markdown
- **`ENTRYPOINT`** defines the main, fixed executable for the container (e.g., `python`) that always runs upon startup.
- **`CMD`** provides default arguments for the `ENTRYPOINT` (e.g., `app.py`), or sets the full default command if `ENTRYPOINT` is omitted.
- Any additional arguments appended to `docker run` **completely override `CMD`**, passing those new arguments directly to `ENTRYPOINT`.

```

---

## Question 6. Data Persistence: Volumes vs Bind Mounts (Practical)

1. Create a named Docker volume called `pg_data_test`.
2. Run a `postgres:17-alpine` container with this volume mounted to `/var/lib/postgresql/data`.
3. Stop and remove the container, then start a new container using the exact same volume.
4. Which CLI command allows you to inspect detailed information (including the host mount path) about the created volume?

**My answer:**
```bash
docker run -d \
  -v pg_data_test:/var/lib/postgresql/data \
  -p 5433:5432 \
  -e POSTGRES_PASSWORD=secret123 \
  --rm \
  postgres:17-alpine

docker stop $(docker ps)

docker run -d \
  -v pg_data_test:/var/lib/postgresql/data \
  -p 5433:5432 \
  -e POSTGRES_PASSWORD=secret123 \
  --rm \
  postgres:17-alpine

docker stop $(docker ps)

docker volume inspect pg_data_test
[
    {
        "CreatedAt": "2026-08-10T09:50:34Z",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/pg_data_test/_data",
        "Name": "pg_data_test",
        "Options": null,
        "Scope": "local"
    }
] 



```

---

## Question 7. Docker Build Optimization & Layer Caching (Theoretical)

Why is it considered a best practice in a Python application `Dockerfile` to structure instructions like this:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Instead of:

```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

**My answer:**
```markdown
Dependencies change far less frequently than application source code. By copying requirements.txt and running pip install before copying the rest of the project, Docker reuses the cached dependency layer whenever only code files change.

In contrast, placing COPY . . first invalidates the cache on every code edit, forcing Docker to re-download and reinstall all Python packages during every build.

```

---

## Question 8. Interacting with a Running Container (Practical)

Given a running PostgreSQL container named `postgres`:
1. Use `docker exec` to start an interactive shell session running the `psql` client as user `postgres`.
2. List all existing databases inside PostgreSQL.

**My answer:**
```bash
# Paste your commands here:

```

---

## Question 9. Docker Networks without Docker Compose (Practical)

1. Create a custom Docker network named `demo_network`.
2. Verify using the Docker CLI that the network exists.
3. Run two `alpine` containers (e.g., named `app1` and `app2`) on this network, and execute `ping app1` from inside `app2`.

**My answer:**
```bash
# Paste your commands here:

```

---

## Question 10. Terraform State File (Theoretical)

What is the `terraform.tfstate` file? Why should you **never** edit it manually and generally avoid committing it to public Git repositories?

**My answer:**
```markdown
# Write your explanation here:

```

---

## Question 11. Terraform Variables and Outputs (Practical)

Write a simple `main.tf` file or HCL snippet that:
1. Defines a variable `project_id` of type `string` with a default value of `"my-gcp-project"`.
2. Defines an `output` block that displays the value of `project_id` after running `terraform apply`.

**My answer:**
```hcl
# Paste your HCL code here:

```

---

## Question 12. Terraform Formatting and Validation (Practical)

Which two Terraform CLI commands are used to:
1. Automatically reformat all `.tf` files in the current directory to match HashiCorp canonical style conventions?
2. Check whether the configuration is syntactically valid and internally consistent without connecting to cloud APIs?

**My answer:**
```bash
# Paste your commands here:

```

---

## Question 13. Terraform Dependencies: Implicit vs Explicit (Theoretical)

What is the difference between an **implicit dependency** and an **explicit dependency** in Terraform? In what situation must you explicitly use the `depends_on` argument?

**My answer:**
```markdown
# Write your explanation here:

```

---

## Question 14. Resource Targeting in Terraform (Practical)

You have a Terraform state containing 10 resources, but you want to run `terraform apply` targeting only a single resource named `google_bigquery_dataset.stg_dataset`. Which flag do you append to the command?

**My answer:**
```bash
# Paste your command here:

```

---

## Question 15. Terraform Remote Backend & State Locking (Theoretical)

What are the primary advantages of using a remote backend (e.g., Google Cloud Storage) instead of storing `terraform.tfstate` locally on your machine? What is **state locking** and why is it important?

**My answer:**
```markdown
# Write your explanation here:

```