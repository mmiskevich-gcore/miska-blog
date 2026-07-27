#!/bin/sh
# Sync this repo's contents to the miska.blog origin VM and reload nginx if needed.
set -e

KEY="${MISKA_BLOG_KEY:-$HOME/.ssh/miska-blog-vm}"
HOST="ubuntu@83.229.15.54"
REMOTE_ROOT="/var/www/miska.blog"
DIR="$(cd "$(dirname "$0")" && pwd)"

rsync -avz --delete \
  --exclude '.git' --exclude '.github' --exclude '.gitignore' --exclude 'deploy.sh' --exclude 'README.md' --exclude 'scripts' \
  -e "ssh -i $KEY" \
  "$DIR/" "$HOST:/tmp/miska-blog-deploy/"

ssh -i "$KEY" "$HOST" "
  sudo rsync -a --delete /tmp/miska-blog-deploy/ $REMOTE_ROOT/ &&
  sudo chown -R root:root $REMOTE_ROOT &&
  sudo find $REMOTE_ROOT -type f -exec chmod 644 {} \; &&
  sudo find $REMOTE_ROOT -type d -exec chmod 755 {} \; &&
  rm -rf /tmp/miska-blog-deploy &&
  sudo nginx -t
"

echo "Deployed. Verifying..."
curl -s -o /dev/null -w "http://miska.blog -> %{http_code}\n" http://miska.blog/
