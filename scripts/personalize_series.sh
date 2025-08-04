#!/usr/bin/env bash
set -euo pipefail
##cReate event tracker -> tv_series_event_tracker


# 1. Çevresel değişkenler
SOLUTION_ARN="arn:aws:personalize:us-east-1:708778582346:solution/tv-series-similar-items-solution"
CAMPAIGN_NAME="tv-series-campaign"
MIN_TPS=1

# --- SolutionVersion Oluştur ve Süresini Ölç ---
echo "=> Creating SolutionVersion..."
sol_start=$(date +%s)

create_output=$(aws personalize create-solution-version \
  --solution-arn "$SOLUTION_ARN" \
  --training-mode FULL)
SOLUTION_VERSION_ARN=$(echo "$create_output" | jq -r '.solutionVersionArn')
echo "   SolutionVersion ARN: $SOLUTION_VERSION_ARN"

status=""
until [[ "$status" == "ACTIVE" ]]; do
  sleep 30
  status=$(aws personalize describe-solution-version \
    --solution-version-arn "$SOLUTION_VERSION_ARN" \
    --query 'solutionVersion.status' --output text)
  if [[ "$status" == "CREATE FAILED" ]]; then
    echo "ERROR: SolutionVersion creation failed" >&2
    exit 1
  fi
done

sol_end=$(date +%s)
sol_duration=$((sol_end - sol_start))
echo "✔ SolutionVersion ACTIVE"
echo "$sol_duration"   # Saniye cinsinden

# --- Campaign Oluştur ve Süresini Ölç ---
echo "=> Creating Campaign..."
camp_start=$(date +%s)

campaign_output=$(aws personalize create-campaign \
  --name "$CAMPAIGN_NAME" \
  --solution-version-arn "$SOLUTION_VERSION_ARN" \
  --min-provisioned-tps $MIN_TPS)
CAMPAIGN_ARN=$(echo "$campaign_output" | jq -r '.campaignArn')
echo "   Campaign ARN: $CAMPAIGN_ARN"

campaign_status=""
until [[ "$campaign_status" == "ACTIVE" ]]; do
  sleep 30
  campaign_status=$(aws personalize describe-campaign \
    --campaign-arn "$CAMPAIGN_ARN" \
    --query 'campaign.status' --output text)
  if [[ "$campaign_status" == "CREATE FAILED" ]]; then
    echo "ERROR: Campaign creation failed" >&2
    exit 1
  fi
done

camp_end=$(date +%s)
camp_duration=$((camp_end - camp_start))
echo "✔ Campaign ACTIVE"
echo "$camp_duration"  # Saniye cinsinden
