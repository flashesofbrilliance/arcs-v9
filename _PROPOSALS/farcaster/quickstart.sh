#!/usr/bin/env bash
# Farcaster read-node quickstart, commands 0 (provision) and 1 (snapchain-bootstrap).
# Usage: quickstart.sh --dry-run | quickstart.sh --create | quickstart.sh --teardown
# --dry-run prints every command and creates nothing. --create refuses while the bootstrap pin is a placeholder.
set -euo pipefail

MODE="${1:-}"
REGION="${AWS_REGION:-us-east-1}"
ITYPE="m5.xlarge"            # 4 vCPU, 16 GB
DISK_GB=2200                 # ~2 TB gp3, check the AWS calculator before --create
NAME="fc-readnode"
# Pinned to a commit so the script cannot change under the reader. PLACEHOLDER until verified against the real repo.
BOOTSTRAP_REPO="https://github.com/farcasterxyz/snapchain"
BOOTSTRAP_COMMIT="PIN_ME_TO_A_VERIFIED_COMMIT_SHA"

run() { if [ "$MODE" = "--dry-run" ]; then printf 'DRY-RUN: %s\n' "$*"; else eval "$*"; fi; }

case "$MODE" in
  --dry-run|--create)
    if [ "$MODE" = "--create" ] && [ "$BOOTSTRAP_COMMIT" = "PIN_ME_TO_A_VERIFIED_COMMIT_SHA" ]; then
      echo "REFUSING: bootstrap commit is still a placeholder" >&2; exit 2
    fi
    echo "# --- teardown (paired with create; also run by '$0 --teardown') ---"
    echo "# aws ec2 terminate-instances --region $REGION --instance-ids \$IID"
    echo "# aws ec2 delete-volume --region $REGION --volume-id \$VOL   # if not DeleteOnTermination"
    echo "# --- command 0: provision ---"
    run "aws budgets describe-budgets --account-id \"\$(aws sts get-caller-identity --query Account --output text)\"   # confirm \$25/\$75 alerts exist first"
    run "IID=\$(aws ec2 run-instances --region $REGION --instance-type $ITYPE --image-id \"\$AMI_ID\" --key-name \"\$KEY_NAME\" --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=$DISK_GB,VolumeType=gp3,DeleteOnTermination=true}' --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=teardown_by,Value=2026-10-26}]' --query 'Instances[0].InstanceId' --output text)"
    run "aws ec2 wait instance-running --region $REGION --instance-ids \"\$IID\""
    echo "# --- command 1: snapchain-bootstrap (runs on the instance) ---"
    run "ssh \"ubuntu@\$HOST\" 'git clone $BOOTSTRAP_REPO snapchain && cd snapchain && git checkout $BOOTSTRAP_COMMIT && ./bootstrap.sh'   # script name unverified"
    ;;
  --teardown)
    : "${IID:?set IID}"
    eval "aws ec2 terminate-instances --region $REGION --instance-ids $IID"
    ;;
  *) echo "usage: $0 --dry-run | --create | --teardown" >&2; exit 64 ;;
esac
