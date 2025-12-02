# Local Service Marketplace (ms-freelancer)

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)
![Vue.js](https://img.shields.io/badge/frontend-Vue.js%203-green)
![AWS EKS](https://img.shields.io/badge/deployment-AWS%20EKS-orange)

## 📖 Project Overview

The **LocalSericeMarketplace** platform is a comprehensive cloud-native microservices-based marketplace designed to connect service providers (e.g., cleaners, plumbers, electricians) with customers seeking on-demand professional services.

The solution addresses inefficiencies in the gig economy by providing a unified platform with structured order workflows, secure payments (escrow-like functionality), and quality assurance through a review system.

### Key Capabilities
* **User Management:** distinct profiles for Customers and Service Providers.
* **Service Marketplace:** Location-based search and skill filtering (static Location).
* **Order Lifecycle:** Full state machine implementation (Pending -> Accepted -> In Progress -> Completed).
* **Secure Payments:** Wallet system with transaction history and refunds.
* **Trust System:** Review and rating logic with content moderation.
* **Notifications:** Multi-channel alerts (Email/Push) driven by domain events.

---

## 🏗 Architecture

The system follows **Domain-Driven Design (DDD)** principles and utilizes a **5-layer architecture**. It is deployed as a set of independent microservices orchestrated by **Kubernetes (EKS)**.

### Microservices (Bounded Contexts)
The system is decomposed into 7 core microservices:

| Service | Responsibility | Database (Polyglot) |
| :--- | :--- | :--- |
| **Gateway** | Unified entry point, Rate Limiting, Routing | Redis (Caching) |
| **Auth** | Identity, JWT Management, RBAC | MySQL (RDS) |
| **User** | Profiles, Skills, Portfolios | MongoDB (Atlas) |
| **Order** | Order Lifecycle, Provider Assignment | MySQL (RDS) |
| **Payment** | Transactions, Refunds, Gateway Integration | MySQL (RDS) |
| **Review** | Ratings, Comments, Moderation | MongoDB (Atlas) |
| **Notification**| Centralized Event Consumption & Delivery | MongoDB (Atlas) |

### Event-Driven Design
We utilize **RabbitMQ** to handle inter-service communication asynchronously. This enables **choreography-based sagas** for distributed transactions (e.g., *Order Completed* event triggers *Payment Processing* and *Review Enablement*).

---

## 🛠 Technology Stack

### Backend & Core
* **Language:** Python 3.11+
* **Framework:** FastAPI (Async support, Pydantic validation)
* **Documentation:** OpenAPI (Swagger UI)

### Frontend
* **Framework:** Vue.js 3 (SPA)
* **Hosting:** AWS Amplify / S3 + CloudFront

### Infrastructure & DevOps
* **Cloud Provider:** AWS (VPC, RDS, DocumentDB, ElastiCache)
* **Container Orchestration:** Amazon EKS (Elastic Kubernetes Service)
* **IaC:** Terraform (Infrastructure provisioning)
* **CI/CD:** GitHub Actions (Monorepo strategy)
* **Security:** AWS WAF, Bandit (SAST), Snyk (SCA)

### Observability & Testing
* **Monitoring:** Amazon CloudWatch (Logs & Dashboards)
* **Performance:** Grafana k6 (Load testing)
* **Testing:** pytest, flake8, black

---

## 🚀 Getting Started

### Prerequisites
* Docker & Docker Compose
* Python 3.11+ & Poetry
* Node.js 18+ (for Frontend)
* AWS CLI (configured) & kubectl

### Installation (Local Dev)

1.  **Backend Setup (Monorepo)**
    Navigate to a specific service (e.g., Auth Service):
    ```bash
    cd services/auth-service
    poetry install
    poetry run uvicorn main:app --reload --port 8001
    ```

2.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Infrastructure**
    Infrastructure is managed via Terraform.
    ```bash
    cd infrastructure/terraform
    terraform init
    terraform plan
    terraform apply
    ```

---

## 🧪 Testing & Quality

### Unit & Integration Testing
We use **pytest** for backend logic. Coverage reports are generated automatically in the CI pipeline.
```bash
# Run tests for a specific service
pytest services/order-service/tests
'''
