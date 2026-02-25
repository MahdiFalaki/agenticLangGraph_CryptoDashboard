# Interview Guide for Crypto Analysis Dashboard

This guide explains the practical architecture and operations in this repo, especially for interview preparation.

## 1) GitHub Workflows Explained (CI/CD)

You have **two GitHub Actions workflows** in `.github/workflows/`:

- `backend-deploy.yml`
- `frontend-deploy.yml`

They automate deployment whenever relevant code paths change on `main`.

### 1.1 Backend workflow (`backend-deploy.yml`)

**Purpose:** Build and deploy backend container updates.

**Trigger behavior:**
- Runs on pushes to `main` when backend files/workflow files change.
- Can also be run manually with `workflow_dispatch`.

**Logical flow:**
1. **Checkout code** from GitHub so the runner has the repository content.
2. **Configure AWS credentials** using OIDC role assumption.
   - This avoids storing long-lived static AWS keys in CI.
3. **Login to Amazon ECR** (Elastic Container Registry).
4. **Build Docker image** from `backend/Dockerfile`.
5. **Tag and push image** to ECR with:
   - commit SHA tag (immutable version marker)
   - `latest` tag (convenience/latest pointer)
6. **Trigger App Runner deployment** to roll the backend service to the new image.

**Why this is valuable in interviews:**
- Demonstrates container CI/CD, cloud registry publishing, and managed service redeploy flow.
- Shows secure AWS auth pattern (OIDC + role assume).

### 1.2 Frontend workflow (`frontend-deploy.yml`)

**Purpose:** Build frontend static assets and publish to CDN-backed hosting.

**Trigger behavior:**
- Runs on pushes to `main` when frontend files/workflow file changes.
- Manual trigger enabled via `workflow_dispatch`.

**Logical flow:**
1. **Checkout code**.
2. **Setup Node** (pin runtime version for consistent builds).
3. **Install dependencies** with `npm ci` (deterministic install from lockfile).
4. **Build** static production assets via Vite.
5. **Configure AWS credentials** with OIDC.
6. **Sync build output to S3** bucket (`aws s3 sync ... --delete`).
7. **Invalidate CloudFront cache** so users get newly deployed assets.

**Why this is valuable in interviews:**
- Demonstrates static-site deployment best practice (build artifacts + object storage + CDN).
- Shows cache invalidation awareness after deploy.

---

## 2) Docker for Newcomers (Backend Dockerfile Deep Explanation)

File: `backend/Dockerfile`

A **Dockerfile** is a recipe to build a portable runtime image. Think of it like a reproducible mini-VM layer stack, but lighter than a full VM.

### 2.1 Line-by-line meaning

1. `FROM python:3.11-slim`
   - Starts from an official lightweight Python base image.
   - Benefit: small image + known Python version.

2. `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1`
   - `PYTHONDONTWRITEBYTECODE=1`: avoids `.pyc` generation in container runtime.
   - `PYTHONUNBUFFERED=1`: logs appear immediately (important in cloud logs).
   - `PIP_NO_CACHE_DIR=1`: reduces image bloat from pip cache.

3. `WORKDIR /app`
   - Sets default working directory for subsequent commands.

4. `COPY backend/requirements.txt /app/backend/requirements.txt`
   - Copies only dependency manifest first.
   - This improves Docker layer caching for faster rebuilds.

5. `RUN pip install -r /app/backend/requirements.txt`
   - Installs Python dependencies into the image.

6. `COPY backend /app/backend`
   - Copies the application code after dependencies.
   - If code changes but requirements do not, dependency layer can stay cached.

7. `EXPOSE 8000`
   - Documents that app listens on port 8000.
   - (It doesn’t publish the port by itself; runtime/paaS maps ports.)

8. `CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]`
   - Launch command when container starts.
   - `0.0.0.0` is critical in containers/cloud so external traffic can reach the app.

### 2.2 Core Docker concepts you should know for interviews

- **Image**: immutable artifact built from Dockerfile.
- **Container**: running instance of an image.
- **Layer caching**: order Dockerfile commands to avoid unnecessary rebuilds.
- **Registry**: where images are stored (ECR here).
- **Tagging**: version labels (SHA and `latest` used here).
- **Runtime config**: secrets/env vars should be injected at runtime, not hardcoded in image.

---

## 3) Frontend Basics You Need (React + MUI)

### 3.1 React essentials visible in this codebase

- The app is component-based (`App.jsx`, `OverviewTab`, `AskAITab`, `HistoryTab`).
- State is managed using React hooks (`useState`, `useEffect`, `useMemo`).
- Data flow:
  - `App.jsx` holds top-level state and API calls.
  - Child components receive data/handlers via props.
- Conditional rendering is used heavily for loading/error/success UI states.
- Async data fetching is done via `fetch`, with staged loading in overview.

**Interview value:** You can explain one-way data flow, state ownership in parent, and UI decomposition into reusable components.

### 3.2 MUI essentials visible in this codebase

- MUI provides prebuilt, theme-aware UI primitives (`Paper`, `Typography`, `Grid`, `Stack`, `Button`, etc.).
- Styling is done with the `sx` prop for concise inline system styling.
- Responsive layout patterns use MUI Grid breakpoints.

**Main benefits of MUI:**
- Faster UI development with consistent design language.
- Accessibility-friendly defaults.
- Responsive utilities out of the box.
- Easier design consistency vs hand-rolling every CSS component.

### 3.3 What to say in interview from this code

- Frontend supports **staged overview loading** (`market -> summary_text -> news`) for better perceived performance.
- UI gracefully handles empty/loading/error states across tabs.
- App includes guided UX cues and structured tab workflows.
- API base URL is environment-driven (`VITE_API_BASE_URL`) for deploy portability.

---

## 4) How Frontend Hosting Works Here

1. Frontend code is built into static files (`npm run build`).
2. Build output is uploaded to an S3 bucket.
3. CloudFront sits in front of S3 and serves assets globally over HTTPS.
4. After deployment, CloudFront invalidation clears cached files.

**Why this architecture:**
- Low-cost, scalable static hosting.
- Fast global delivery via CDN.
- Clear separation between frontend static delivery and backend API compute.

---

## 5) How Backend Hosting Works Here

1. Backend is packaged as a Docker image.
2. CI pushes image to ECR.
3. AWS App Runner runs the containerized FastAPI service.
4. App Runner exposes public API endpoint.
5. Health endpoints (`/health`, `/health/deps`) support runtime checks.
6. Runtime secrets/config are injected via environment/secret mechanisms.

**Why this architecture:**
- Simplifies operations vs self-managing Kubernetes/EC2.
- Keeps deployment reproducible and image-based.
- Good fit for portfolio and early production-grade services.

---

## 6) Honest Professional Positioning

You can truthfully claim:
- Practical cloud CI/CD and deployment delivery.
- Containerized backend operations.
- CDN-based static hosting and cache invalidation.

You should **not overclaim** mature enterprise DevOps coverage unless you also add:
- full IaC lifecycle (Terraform/CDK/CloudFormation),
- multi-env promotion strategy,
- canary/blue-green rollout automation,
- centralized observability/alerting SLO stack,
- compliance/security automation depth.
