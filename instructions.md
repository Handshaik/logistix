# Technical Interview

## Scenario

We are building a delivery system for a logistics centre. This centre has its own group of drivers. Every day we receive a list of drivers with a set of assignments they need.

At the start of each day, we get two lists (see [rules.py](rules.py) for how these are generated):

1. **Drivers** – each with a unique `driver_id` and a set of operational rules (regions, weight limits, temperature control, etc.)
2. **Packages** – each with a unique `package_id` and attributes (weight, perishability, region, distance, hazmat class, volume, etc.)

Each driver may only handle packages that satisfy *all* of their rules. If a driver has no rules for a given attribute, that attribute is ignored.

---

## Endpoints

### `POST /assign`

**Purpose**: Assign up to `max_per_driver` packages to each driver and record an initial status of `assigned` in DynamoDB.

**Request**

```json
{
  "driver_ids": ["driver_1", "driver_2", "driver_3"],
  "max_per_driver": 10
}
```

**Response**

```json
{
  "assignments": {
    "driver_1": ["<pkg‑uuid1>", "<pkg‑uuid2>", …],
    "driver_2": ["<pkg‑uuid3>", …],
    "driver_3": []
  },
  "unassigned_packages": ["<pkg‑uuid4>", …],
  "unassigned_drivers": ["driver_3"]
}
```

Behavior:

* Filter packages per driver by their rules.
* Assign up to `max_per_driver` matching packages to each driver.
* Write an item per assignment in DynamoDB table `DeliveryAssignments` with keys:

  * **Partition key**: `driver_id`
  * **Sort key**: `package_id`
  * **Attribute**: `status` = `assigned`

---

### `POST /update`

**Purpose**: Update the delivery status of a specific driver/package pair in DynamoDB.

**Example Request**

```json
{
  "driver_id": "driver_1",
  "package_id": "413a59e3-2583-4263-8e1c-8c5a632d03ae",
  "status": "in_progress"
}
```

Behavior:

* Look up the existing item by (`driver_id`, `package_id`).
* Update its `status` attribute to one of: `assigned`, `accepted`, `in_progress`, `delivered`, `failed_to_deliver`.
* **Response**: HTTP 200 on success; HTTP 404 if the record does not exist.

---

## Infrastructure Requirements

* **LocalStack** emulation (via `docker-compose.yml`) for:
  * **DynamoDB** (primary data store)
  * **S3** (optional logging bucket)

* **Terraform** in `infra/` to provision:

  * DynamoDB table `DeliveryAssignments`
  * (Stretch) S3 bucket for logging
  * Workspaces for Dev/Test/Prod
* **Docker Compose** service snippet provided below.

**`docker-compose.yml`**

```yaml
version: "3.8"

services:
  localstack:
    image: localstack/localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb
      - DEBUG=1
    volumes:
      - localstack_data:/var/lib/localstack
    healthcheck:
      test: ["CMD","curl","-f","http://localhost:4566/_localstack/health"]
      interval: 5s
      retries: 10

volumes:
  localstack_data:
```

**`rules.py`**

The scripts in the file can be used to generate driver rules and packages for each day.

---

## Makefile

```makefile
.PHONY: up down build terraform-init terraform-apply test

up:
	docker-compose up --build

down:
	docker-compose down

build:
	docker-compose build

terraform-init:
	cd infra && terraform init

terraform-apply:
	cd infra && terraform apply -auto-approve

test:
	curl -X POST http://localhost:8000/assign \
	  -H "Content-Type: application/json" \
	  -d '{"driver_ids":["driver_1","driver_2"],"max_per_driver":2}'
```

---

## Stretch Goals

* Implement CI with GitHub Actions (`make test`, `make terraform-apply`).
* Add operational logs (assignments & updates) to an S3 bucket.
* Include richer package metadata (destination address, weight, volume) in DynamoDB items.
* Add retry/backoff logic for DynamoDB outages.
* Add testing.

---

### Notes

* **DynamoDB table schema**:

  * Partition key: `driver_id`
  * Sort key: `package_id`
  * Attribute: `status`

Good luck!
