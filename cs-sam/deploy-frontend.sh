#!/usr/bin/env bash
# Build the Vue frontend and publish it to the stack's S3 bucket + CloudFront.
#
# Usage (from anywhere):
#   ./deploy-frontend.sh [aws-profile]
#
# The profile can also come from AWS_PROFILE. Override the stack/region with
# STACK_NAME / AWS_REGION (defaults match samconfig.toml).
# Requires the SAM stack to be deployed first (`sam build && sam deploy`).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
STACK_NAME="${STACK_NAME:-cs-sam}"
REGION="${AWS_REGION:-us-west-2}"
PROFILE="${1:-${AWS_PROFILE:-}}"

aws_args=(--region "$REGION")
if [[ -n "$PROFILE" ]]; then
  aws_args+=(--profile "$PROFILE")
fi

for cmd in aws npm; do
  command -v "$cmd" >/dev/null || { echo "Error: '$cmd' not found on PATH." >&2; exit 1; }
done

stack_output() {
  aws cloudformation describe-stacks "${aws_args[@]}" --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}

ACCOUNT="$(aws sts get-caller-identity "${aws_args[@]}" --query Account --output text)"
echo "==> Account $ACCOUNT, region $REGION, stack $STACK_NAME${PROFILE:+, profile $PROFILE}"

BUCKET="$(stack_output FrontendBucketName)"
DIST_ID="$(stack_output DistributionId)"
FRONTEND_URL="$(stack_output FrontendUrl)"
if [[ -z "$BUCKET" || "$BUCKET" == "None" || -z "$DIST_ID" || "$DIST_ID" == "None" ]]; then
  echo "Error: stack '$STACK_NAME' has no FrontendBucketName/DistributionId outputs." >&2
  echo "       Run 'sam build && sam deploy' first." >&2
  exit 1
fi
echo "==> Bucket $BUCKET, distribution $DIST_ID"

echo "==> Building frontend"
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then
  npm ci
fi
npm run build
[[ -f dist/index.html ]] || { echo "Error: build produced no dist/index.html" >&2; exit 1; }

echo "==> Uploading to s3://$BUCKET"
# Hashed assets never change under the same name: cache for a year.
aws s3 sync dist/assets "s3://$BUCKET/assets" "${aws_args[@]}" --delete \
  --cache-control "public,max-age=31536000,immutable"
# index.html, favicon, etc.: always revalidate so new deploys show up immediately.
aws s3 sync dist "s3://$BUCKET" "${aws_args[@]}" --delete --exclude "assets/*" \
  --cache-control "no-cache"

echo "==> Invalidating CloudFront cache"
INVALIDATION_ID="$(aws cloudfront create-invalidation "${aws_args[@]}" --distribution-id "$DIST_ID" \
  --paths "/index.html" "/" --query Invalidation.Id --output text)"
echo "    Invalidation $INVALIDATION_ID submitted (usually completes within a minute or two)"

echo "==> Done: $FRONTEND_URL"
