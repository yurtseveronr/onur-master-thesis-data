#!/usr/bin/env bash
set -euo pipefail

CLUSTER="onur-master-eks"
REGION="us-east-1"
ACCOUNT_ID="708778582346"
POLICY_NAME="AWSLoadBalancerControllerIAMPolicy"
APP_TAG="v2.13.3"

POLICY_ARN=$(aws iam list-policies --scope Local \
  --query "Policies[?PolicyName=='${POLICY_NAME}'].Arn" --output text)
if [[ -z "$POLICY_ARN" ]]; then
  echo "Policy ${POLICY_NAME} not found. Create it first with the official iam_policy.json." >&2
  exit 1
fi
echo "Using policy: $POLICY_ARN"


curl -sS -o iam_policy.json \
  "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/${APP_TAG}/docs/install/iam_policy.json"


#  - elasticloadbalancing:DescribeListenerAttributes
#  - elasticloadbalancing:ModifyListenerAttributes


VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" \
  --query 'Versions[?IsDefaultVersion==`false`].[VersionId,CreateDate]' --output text | sort -k2 | awk '{print $1}')
COUNT=$(echo "$VERSIONS" | wc -w | tr -d ' ')
if [[ ${COUNT:-0} -ge 4 ]]; then
  OLDEST=$(echo "$VERSIONS" | head -n1)
  aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$OLDEST"
fi


aws iam create-policy-version --policy-arn "$POLICY_ARN" \
  --policy-document file://iam_policy.json --set-as-default >/dev/null
echo "Policy updated to latest (set-as-default)."


kubectl -n kube-system rollout restart deploy/aws-load-balancer-controller
kubectl -n kube-system rollout status deploy/aws-load-balancer-controller


kubectl -n kube-system logs deploy/aws-load-balancer-controller | tail -n 50
