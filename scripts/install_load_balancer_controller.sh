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
  echo "Policy ${POLICY_NAME} not found. Creating it."
  curl -sS -o iam_policy.json \
    "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/${APP_TAG}/docs/install/iam_policy.json"
  aws iam create-policy --policy-name "${POLICY_NAME}" --policy-document file://iam_policy.json
  POLICY_ARN=$(aws iam list-policies --scope Local \
    --query "Policies[?PolicyName=='${POLICY_NAME}'].Arn" --output text)
fi
echo "Using policy: $POLICY_ARN"

# install helm if not available
if ! command -v helm >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

# ensure cluster access
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER"

# create sa ahead of time (pod identity association will bind later)
kubectl create serviceaccount -n kube-system aws-load-balancer-controller --dry-run=client -o yaml | kubectl apply -f -

# add helm repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# install or upgrade aws-load-balancer-controller
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName="$CLUSTER" \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$REGION"

kubectl -n kube-system rollout status deploy/aws-load-balancer-controller --timeout=5m
kubectl -n kube-system logs deploy/aws-load-balancer-controller | tail -n 50
