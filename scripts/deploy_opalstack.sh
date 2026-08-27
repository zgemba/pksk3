#!/usr/bin/env bash
# Deploy a committed branch to the existing Opalstack application.
#
# Usage: ./scripts/deploy_opalstack.sh [branch]
# Environment: OPALSTACK_HOST=opal (default)

set -Eeuo pipefail

branch="${1:-codex/replacement}"
remote_host="${OPALSTACK_HOST:-opal}"

if ! git check-ref-format --branch "$branch" >/dev/null 2>&1; then
    printf 'Invalid Git branch: %s\n' "$branch" >&2
    exit 2
fi

printf 'Deploying branch %s to %s…\n' "$branch" "$remote_host"

ssh "$remote_host" bash -s -- "$branch" <<'REMOTE_SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail

branch="$1"
app_root="/home/zgemba/apps/pksk-ng"
project_dir="$app_root/project"
python_bin="$app_root/env/bin/python"
uwsgi_entrypoint="$project_dir/wsgi.py"
log_dir="/home/zgemba/logs/deployments"
lock_dir="$app_root/tmp/deploy.lock"

mkdir -p "$log_dir" "$app_root/tmp"

if ! mkdir "$lock_dir" 2>/dev/null; then
    printf 'Another deployment is already running.\n' >&2
    exit 1
fi

cleanup() {
    rmdir "$lock_dir"
}
trap cleanup EXIT

log_file="$log_dir/pksk-ng-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee -a "$log_file") 2>&1

cd "$project_dir"

if [[ -n "$(git status --porcelain)" ]]; then
    printf 'Refusing deployment: the server checkout has uncommitted changes.\n' >&2
    exit 1
fi

previous_revision="$(git rev-parse HEAD)"
switched_revision=0
restarted=0

rollback() {
    status=$?
    trap - ERR

    if [[ "$switched_revision" -eq 1 ]]; then
        printf 'Deployment failed; restoring source revision %s.\n' "$previous_revision" >&2
        git checkout -q "$previous_revision" || true

        if [[ "$restarted" -eq 1 ]]; then
            touch "$uwsgi_entrypoint" || true
        fi
    fi

    exit "$status"
}
trap rollback ERR

git fetch --quiet origin "$branch"
candidate_revision="$(git rev-parse FETCH_HEAD)"
printf 'Deploying %s\n' "$candidate_revision"

git checkout -q "$candidate_revision"
switched_revision=1

"$python_bin" -m pip install --disable-pip-version-check -r requirements.txt
"$python_bin" -m compileall -q app wsgi.py

export FLASK_CONFIG=production
export DATABASE_URL="postgresql+psycopg://pkskng@127.0.0.1:5432/pkskng"
export PGPASSFILE="/home/zgemba/.pgpass"

"$python_bin" -c 'from wsgi import app; assert app.config["SQLALCHEMY_DATABASE_URI"]'
"$python_bin" -m flask --app wsgi db upgrade

touch "$uwsgi_entrypoint"
restarted=1
sleep 3
curl --fail --silent --show-error http://127.0.0.1:30291/health

printf '\nDeployment complete: %s\nLog: %s\n' "$candidate_revision" "$log_file"
REMOTE_SCRIPT
