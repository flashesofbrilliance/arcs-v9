#!/usr/bin/env bash
# Farcaster read-node quickstart, commands 0 (provision) and 1 (snapchain-bootstrap). FAIL-CLOSED.
# Usage: quickstart.sh --dry-run | --create | teardown [--verify] [--dry-run]
#   --create refuses unless FC_BUDGET_ALERT_ID is set (the id of a real billing alert); it prints the plan, then refuses while the bootstrap pin is a placeholder.
#   Every resource is tagged fc-bounty=2026-10; teardown is a tag query, not a remembered id.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
ITYPE="m5.xlarge"; DISK_GB=2200; NAME="fc-readnode"; TAG_KEY="fc-bounty"; TAG_VAL="2026-10"
BOOTSTRAP_REPO="https://github.com/farcasterxyz/snapchain"
BOOTSTRAP_COMMIT="PIN_ME_TO_A_VERIFIED_COMMIT_SHA"
tags() { printf 'ResourceType=%s,Tags=[{Key=%s,Value=%s},{Key=Name,Value=%s}]' "$1" "$TAG_KEY" "$TAG_VAL" "$NAME"; }

estimate() {
  echo "# --- estimated cost per resource (nothing is created in this mode) ---"
  echo "# EC2 $ITYPE on-demand: about \$0.192/hr (about \$140/month). UNVERIFIED: from the research brief (aggregator page, July 2026), URL not recorded. Check https://aws.amazon.com/ec2/pricing/on-demand/"
  echo "# EBS gp3 ${DISK_GB} GB: price UNVERIFIED (not sourced). Check https://aws.amazon.com/ebs/pricing/"
  echo "# Data transfer out and snapshots: UNVERIFIED (not sourced)"
  echo "# Planning figure: treat the total as 2x to 3x the \$100/month in Snapchain's own AWS guide until the AWS calculator says otherwise."
}
tagq() { printf 'aws ec2 describe-instances --region %s --filters "Name=tag:%s,Values=%s" "Name=instance-state-name,Values=pending,running,stopping,stopped" --query "Reservations[].Instances[].InstanceId" --output text' "$REGION" "$TAG_KEY" "$TAG_VAL"; }
volq() { printf 'aws ec2 describe-volumes --region %s --filters "Name=tag:%s,Values=%s" --query "Volumes[].VolumeId" --output text' "$REGION" "$TAG_KEY" "$TAG_VAL"; }
plan() {
  estimate
  echo "# --- command 0: provision (all tagged $TAG_KEY=$TAG_VAL) ---"
  echo "PLAN: aws ec2 run-instances --region $REGION --instance-type $ITYPE --image-id \$AMI_ID --key-name \$KEY_NAME --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=$DISK_GB,VolumeType=gp3,DeleteOnTermination=true}' --tag-specifications '$(tags instance)' '$(tags volume)'"
  echo "# --- command 1: snapchain-bootstrap (on the instance) ---"
  echo "PLAN: ssh ubuntu@\$HOST 'git clone $BOOTSTRAP_REPO snapchain && cd snapchain && git checkout $BOOTSTRAP_COMMIT && ./bootstrap.sh'   # bootstrap script name UNVERIFIED"
  echo "# --- paired teardown (tag query) ---"
  echo "PLAN: IDS=\$($(tagq)) && aws ec2 terminate-instances --region $REGION --instance-ids \$IDS"
}

cmd="${1:-}"; shift || true
case "$cmd" in
  --dry-run) plan ;;
  --create)
    if [ -z "${FC_BUDGET_ALERT_ID:-}" ]; then echo "REFUSING: FC_BUDGET_ALERT_ID not set. Create a billing alert first and export its id." >&2; exit 3; fi
    plan
    if [ "$BOOTSTRAP_COMMIT" = "PIN_ME_TO_A_VERIFIED_COMMIT_SHA" ]; then echo "REFUSING TO EXECUTE: bootstrap commit is still a placeholder (plan shown above)" >&2; exit 2; fi
    echo "plan accepted (budget alert $FC_BUDGET_ALERT_ID); execution intentionally not automated in this draft" ;;
  teardown)
    verify=0; dry=0
    for a in "$@"; do case "$a" in --verify) verify=1;; --dry-run) dry=1;; esac; done
    if [ "$verify" = 1 ] && [ "$dry" = 1 ]; then
      echo "FILTER: tag:$TAG_KEY=$TAG_VAL in region $REGION"
      echo "DRY-RUN: $(tagq)"; echo "DRY-RUN: $(volq)"
      echo "EXPECTED after teardown: both queries print nothing (empty)"
    elif [ "$verify" = 1 ]; then eval "$(tagq)"; eval "$(volq)"
    elif [ "$dry" = 1 ]; then echo "DRY-RUN: IDS=\$($(tagq)) && aws ec2 terminate-instances --region $REGION --instance-ids \$IDS"
    else IDS=$(eval "$(tagq)"); [ -n "$IDS" ] && aws ec2 terminate-instances --region "$REGION" --instance-ids $IDS; fi ;;
  *) echo "usage: $0 --dry-run | --create | teardown [--verify] [--dry-run]" >&2; exit 64 ;;
esac
