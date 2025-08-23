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

# Get VPC ID from CloudFormation
echo "Getting VPC ID from CloudFormation..."
VPC_ID=$(aws cloudformation describe-stacks --stack-name network-stack --region "$REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`VPC`].OutputValue' --output text)
echo "VPC ID: $VPC_ID"

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

# Clean up existing helm release if exists
echo "Cleaning up existing helm release..."
kubectl delete deployment aws-load-balancer-controller -n kube-system --ignore-not-found=true || true
kubectl delete pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --ignore-not-found=true || true
helm uninstall aws-load-balancer-controller -n kube-system || true

# Force delete helm release if it still exists
echo "Force deleting helm release..."
helm delete aws-load-balancer-controller -n kube-system --no-hooks || true
kubectl delete secret -n kube-system sh.helm.release.v1.aws-load-balancer-controller.v1 --ignore-not-found=true || true
kubectl delete secret -n kube-system sh.helm.release.v1.aws-load-balancer-controller.v2 --ignore-not-found=true || true
kubectl delete secret -n kube-system sh.helm.release.v1.aws-load-balancer-controller.v3 --ignore-not-found=true || true

sleep 10

# install aws-load-balancer-controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName="$CLUSTER" \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$REGION" \
  --set vpcId="$VPC_ID" \
  --wait \
  --timeout=10m

# Wait for deployment with longer timeout and better error handling
echo "Waiting for AWS Load Balancer Controller deployment..."
kubectl -n kube-system rollout status deploy/aws-load-balancer-controller --timeout=10m || {
  echo "⚠️ Rollout status timeout, checking deployment status..."
  kubectl get pods -n kube-system | grep aws-load-balancer-controller
  kubectl describe deployment aws-load-balancer-controller -n kube-system
  echo "Showing recent logs..."
  kubectl -n kube-system logs deploy/aws-load-balancer-controller --tail=50 || echo "No logs available"
  echo "Continuing with deployment..."
}
