# Terraform & HCL Reference Guide

## 1. Introduction to Terraform & Infrastructure as Code (IaC)

**Terraform** is an open-source **Infrastructure as Code (IaC)** tool created by HashiCorp. It enables cloud engineers and DevOps professionals to safely and predictably create, modify, and destroy infrastructure resources across multiple cloud providers and on-premises environments using declarative configuration files.

### Key Concepts & Benefits

*   **Declarative Approach:** You describe the *desired end state* of your infrastructure in configuration files. Terraform determines the underlying dependencies and necessary API calls to reach that state, unlike imperative tools that require step-by-step instructions.
*   **Multi-Cloud Management:** Provides a single, unified language (**HCL**) and consistent workflow to manage infrastructure across AWS, Azure, Google Cloud Platform (GCP), Kubernetes, Docker, VMware, and hundreds of SaaS providers.
*   **State Management:** Terraform tracks real-world infrastructure state in a state file (`terraform.tfstate`). This enables drift detection, precise update planning, and safe resource modifications.
*   **Idempotency:** Applying the same configuration multiple times results in the exact same infrastructure state without unnecessary duplicate creations or broken dependencies.

---

## 2. Terraform Architecture & Core Lifecycle

### The Terraform Lifecycle

The core Terraform workflow consists of four fundamental stages:

```
+------------------+     +-------------------+     +--------------------+     +-------------------+
|  terraform init  | --> |  terraform plan   | --> |  terraform apply   | --> | terraform destroy |
| (Initialize Dir) |     | (Preview Changes) |     | (Execute Provision)|     | (Tear Down All)   |
+------------------+     +-------------------+     +--------------------+     +-------------------+
```

1.  `terraform init`
    *   **Purpose:** Initializes a working directory containing Terraform configuration files.
    *   **Actions:** Downloads and installs necessary provider plugins (e.g., AWS, Docker), installs declared modules, and sets up the backend for state storage.
2.  `terraform plan`
    *   **Purpose:** Generates and displays an execution plan without modifying real resources.
    *   **Actions:** Compares the desired configuration against the current state file and real-world infrastructure, creating an execution graph to calculate required actions (`+ create`, `~ update in-place`, `- destroy`, `-/+ replace`).
3.  `terraform apply`
    *   **Purpose:** Executes the actions proposed in the execution plan.
    *   **Actions:** Calls provider APIs to provision or modify infrastructure. Prompts for user confirmation (unless `-auto-approve` is passed) and updates the `terraform.tfstate` file upon completion.
4.  `terraform destroy`
    *   **Purpose:** Deletes all resources managed by the current Terraform project state.
    *   **Actions:** Reverses the execution graph to destroy infrastructure safely in reverse dependency order.

---

## 3. HCL (HashiCorp Configuration Language) Syntax & Structure

HCL is a human-readable, machine-friendly configuration language designed specifically for defining infrastructure.

### General Syntax Block Structure

```hcl
block_type "label_1" "label_2" {
  argument_1 = "string_value"
  argument_2 = 8080
  argument_3 = true

  nested_block {
    nested_argument = ["element_1", "element_2"]
  }
}
```

### Key Components

*   **Block Type:** Defines the purpose of the configuration block (e.g., `resource`, `variable`, `provider`, `data`, `output`, `terraform`, `module`, `local`).
*   **Labels:** Provide specifics for the block. A `resource` block takes two labels (resource type and resource local name), whereas a `variable` block takes one label (variable name).
*   **Arguments:** Assign values to keys (`key = value`) inside the block.
*   **Nested Blocks:** Structurally nested configuration units within a parent block.

---

## 4. HCL Data Types

HCL supports primitive, collection, and structural data types to define schema rules and variable inputs.

### Data Types Overview Table

| Category | Type | Description | Example Syntax |
| :--- | :--- | :--- | :--- |
| **Primitive** | `string` | Sequence of Unicode characters | `"us-east-1"` |
| **Primitive** | `number` | Integer or floating-point value | `8080`, `3.14` |
| **Primitive** | `bool` | Boolean truth value | `true`, `false` |
| **Collection**| `list(<type>)` | Ordered sequence of values of the same type | `["web1", "web2"]` |
| **Collection**| `set(<type>)` | Unordered collection of unique values | `["80", "443"]` |
| **Collection**| `map(<type>)` | Key-value pairs where all values share the same type | `{ env = "prod", owner = "devops" }` |
| **Structural**| `object({...})` | Named attributes with differing specified types | `object({ name = string, port = number })` |
| **Structural**| `tuple([...])` | Fixed-length sequence with differing element types | `tuple([string, number, bool])` |

---

## 5. Managing Variables & Configuration Input

Variables allow Terraform configurations to be dynamic, reusable, and customizable across different environments (e.g., dev, staging, prod).

### Declaring Variables (`variables.tf`)

Variable declarations establish the schema, defaults, constraints, and validation rules.

```hcl
variable "container_count" {
  description = "Number of application containers to deploy"
  type        = number
  default     = 2

  validation {
    condition     = var.container_count > 0
    error_message = "The container_count parameter must be greater than 0."
  }
}

variable "db_password" {
  description = "Master password for the database instance"
  type        = string
  sensitive   = true # Suppresses sensitive value output in CLI console logs
}

variable "app_environment" {
  description = "Target deployment environment"
  type        = string
  default     = "development"
}
```

### Variable Attributes Reference

*   `type`: Enforces the data type allowed for the variable.
*   `default`: Sets a fallback value if no input is provided during execution.
*   `description`: Documenting prompt explaining the variable's intent.
*   `sensitive`: Hides the variable value in `terraform plan` and `terraform apply` console logs. *(Note: State files still contain raw values; store state securely!)*
*   `validation`: Defines custom logical conditions (`condition`) and custom error feedback (`error_message`).
*   `nullable`: Specifies whether the variable accepts `null` values (defaults to `true`).

### Supplying Variable Values (`terraform.tfvars`)

While `variables.tf` defines the variable schema, values are assigned via configuration files, environment variables, or CLI flags.

```hcl
# terraform.tfvars
container_count = 5
app_environment = "production"
db_password     = "SuperSecretPassword123!"
```

### Variable Definition Precedence (Highest to Lowest)

1.  CLI `-var` or `-var-file` flags (e.g., `terraform apply -var="container_count=3"`)
2.  `*.auto.tfvars` or `*.auto.tfvars.json` files (processed in alphabetical order)
3.  `terraform.tfvars` or `terraform.tfvars.json` file
4.  `TF_VAR_name` environment variables (e.g., `export TF_VAR_db_password="Secret"`)
5.  Default values set inside `variables.tf`

### Referencing Variables in Configuration

Variables are accessed using the `var.<variable_name>` interpolation syntax.

```hcl
resource "docker_container" "app" {
  count = var.container_count
  name  = "app-instance-${count.index + 1}"
  image = "nginx:latest"
}
```

---

## 6. Exposing Data with Outputs (`outputs.tf`)

Outputs highlight important infrastructure details after deployment (such as IP addresses, DNS endpoints, database connection strings) and make them accessible to external scripts or parent modules.

```hcl
output "container_names" {
  description = "List of created Docker container names"
  value       = docker_container.app[*].name
}

output "database_endpoint" {
  description = "Connection string for the database"
  value       = "db.example.com:5432"
  sensitive   = true # Conceals output in CLI output
}
```

---

## 7. Terraform CLI Command Reference

### Core Workflow Commands

*   `terraform init` — Initializes working directory, fetches modules, downloads provider plugins.
*   `terraform plan` — Previews infrastructure additions, updates, or deletions.
*   `terraform apply` — Provisions infrastructure according to execution plans.
*   `terraform destroy` — Tears down all managed infrastructure.

### Maintenance & Code Quality Commands

*   `terraform fmt` — Automatically formats `.tf` code files according to standard HCL styling guidelines.
*   `terraform validate` — Checks syntax and internal consistency of configuration files without calling remote APIs.
*   `terraform show` — Displays a human-readable output of the current state or a plan file.
*   `terraform state list` — Lists all resources currently tracked in the state file.
*   `terraform state show <resource_address>` — Shows attributes of a specific resource in state.
*   `terraform import <resource_address> <id>` — Imports existing infrastructure into Terraform state without destroying it.
*   `terraform workspace list` / `select` / `new` — Manages isolated state environments within the same working directory.

---

## 8. Complete Practical Example: Docker Infrastructure

Here is a complete, production-ready example demonstrating the relationship between top-level configuration blocks (`terraform {}`), providers (`provider {}`), resources (`resource {}`), variables (`variable {}`), and outputs (`output {}`).

```hcl
# main.tf

# 1. Terraform Settings Block
# Configures core Terraform settings, required version, and provider constraints
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

# 2. Provider Block
# Configures the specific provider plugin (Docker in this case)
provider "docker" {
  host = "unix:///var/run/docker.sock" # Docker daemon connection
}

# 3. Input Variables
variable "container_name" {
  description = "Name of the Docker container"
  type        = string
  default     = "my-nginx-webserver"
}

variable "host_port" {
  description = "External port mapped on the host machine"
  type        = number
  default     = 8080
}

# 4. Resource Blocks
# Downloads the NGINX Docker image
resource "docker_image" "nginx" {
  name         = "nginx:latest"
  keep_locally = false
}

# Creates and starts the NGINX container
resource "docker_container" "nginx_app" {
  name  = var.container_name
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = var.host_port
  }
}

# 5. Output Declarations
output "container_id" {
  description = "ID of the created Docker container"
  value       = docker_container.nginx_app.id
}

output "web_url" {
  description = "URL to access the NGINX web server"
  value       = "http://localhost:${var.host_port}"
}
```

---

## 9. Key Takeaways & Best Practices

1.  **Block Purpose Summary:**
    *   `terraform {}`: Sets requirement constraints for Terraform CLI version and required providers.
    *   `provider {}`: Configures credentials, endpoints, and settings for a specific cloud/service plugin.
    *   `resource {}`: Defines infrastructure components to manage (VMs, networks, containers).
    *   `data {}`: Fetches read-only data from external or existing infrastructure.
    *   `variable {}`: Declares input parameters to make configurations reusable.
    *   `output {}`: Exposes values produced by resources.
2.  **Version Pinning:** Always pin provider versions using pessimistic constraint operators (`~> 3.0`) to avoid breaking API changes in automated pipelines.
3.  **State Security:** Never commit `.tfstate` files or `terraform.tfvars` containing secrets to public Git repositories. Add `.tfstate`, `*.tfvars`, and `.terraform/` to `.gitignore`.