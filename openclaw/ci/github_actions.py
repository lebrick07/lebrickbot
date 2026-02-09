from typing import Dict

def generate_github_actions(payload: Dict):
    repo_type = payload.get("repo_type", "node")
    cloud = payload.get("cloud", "aws")
    deploy = payload.get("deploy", "kubernetes")

    ci = f"""
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm test
"""

    deploy = f"""
name: Deploy

on:
  push:
    branches: [ "main" ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{{{ secrets.AWS_ROLE_ARN }}}}
          aws-region: us-east-1

      - name: Deploy via kubectl
        run: kubectl apply -f k8s/
"""

    return {
        "ci.yml": ci.strip(),
        "deploy.yml": deploy.strip(),
        "explanation": "CI builds and tests. Deploy assumes AWS role and applies Kubernetes manifests."
    }
