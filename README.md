# PKSK replacement

Minimal Flask replacement for the PKSK website.

## Local development

Create a Python 3.13 virtual environment, install the dependencies, and run:

```text
pip install -r requirements-dev.txt
flask --app wsgi run --debug
```

The application is currently a runnable scaffold. The implementation plan is documented in [`recap.md`](recap.md).

## Opalstack deployment

Commit and push the branch to GitHub first, then deploy that pushed revision:

```text
./scripts/deploy_opalstack.sh
```

The script deploys `codex/replacement` by default. Pass another branch explicitly when needed:

```text
./scripts/deploy_opalstack.sh branch-name
```

It connects through the `opal` SSH alias, locks the deployment, fetches the selected branch, installs requirements, runs Flask migrations against production PostgreSQL, restarts uWSGI, and verifies `/health`. Deployment logs are stored on Opalstack under `/home/zgemba/logs/deployments/`.

For PyCharm, create an External Tool with program `/bin/bash`, arguments `$ProjectFileDir$/scripts/deploy_opalstack.sh`, and working directory `$ProjectFileDir$`.
