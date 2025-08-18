#!/usr/bin/env bash
set -euo pipefail

: "${REGION:=us-east-1}"
: "${AWS_ACCOUNT_ID:=708778582346}"
: "${STACK_NAME:?Set STACK_NAME}"
: "${USERNAME:=AWSReservedSSO_AdministratorAccess_d58e90fb67f5d77e/onur.yurtsever@commencis.com}"
: "${NAMESPACE:=default}"
QS_USER_ARN="arn:aws:quicksight:${REGION}:${AWS_ACCOUNT_ID}:user/${NAMESPACE}/${USERNAME}"

MOVIES_DS_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='MoviesDataSetArn'].OutputValue" --output text)
SERIES_DS_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='SeriesDataSetArn'].OutputValue" --output text)

echo "Movies DS: $MOVIES_DS_ARN"
echo "Series DS: $SERIES_DS_ARN"

movies_def="$(mktemp)"
series_def="$(mktemp)"
cat >"$movies_def"<<EOF
{
  "DataSetIdentifierDeclarations": [
    { "Identifier": "movies_ds", "DataSetArn": "$MOVIES_DS_ARN" }
  ],
  "Sheets": [
    { "Name": "Movies Sheet", "SheetId": "movies-sheet" }
  ]
}
EOF
cat >"$series_def"<<EOF
{
  "DataSetIdentifierDeclarations": [
    { "Identifier": "series_ds", "DataSetArn": "$SERIES_DS_ARN" }
  ],
  "Sheets": [
    { "Name": "Series Sheet", "SheetId": "series-sheet" }
  ]
}
EOF

create_or_update_analysis () {
  local ANALYSIS_ID="$1"; local NAME="$2"; local DEF_FILE="$3"
  if aws quicksight describe-analysis --aws-account-id "$AWS_ACCOUNT_ID" --analysis-id "$ANALYSIS_ID" --region "$REGION" >/dev/null 2>&1; then
    aws quicksight update-analysis --aws-account-id "$AWS_ACCOUNT_ID" --analysis-id "$ANALYSIS_ID" --name "$NAME" --definition "file://$DEF_FILE" --region "$REGION" >/dev/null
  else
    aws quicksight create-analysis \
      --aws-account-id "$AWS_ACCOUNT_ID" \
      --analysis-id "$ANALYSIS_ID" \
      --name "$NAME" \
      --permissions "[{\"Principal\":\"$QS_USER_ARN\",\"Actions\":[\"quicksight:DescribeAnalysis\",\"quicksight:UpdateAnalysis\",\"quicksight:DeleteAnalysis\",\"quicksight:QueryAnalysis\",\"quicksight:RestoreAnalysis\"]}]" \
      --definition "file://$DEF_FILE" \
      --region "$REGION" >/dev/null
  fi
}

create_or_update_template () {
  local TEMPLATE_ID="$1"; local NAME="$2"; local ANALYSIS_ID="$3"; local DS_ARN="$4"; local PLACEHOLDER="$5"
  local ANALYSIS_ARN
  ANALYSIS_ARN=$(aws quicksight describe-analysis --aws-account-id "$AWS_ACCOUNT_ID" --analysis-id "$ANALYSIS_ID" --query "Analysis.Arn" --output text --region "$REGION")
  local SRC="{\"SourceAnalysis\":{\"Arn\":\"$ANALYSIS_ARN\",\"DataSetReferences\":[{\"DataSetArn\":\"$DS_ARN\",\"DataSetPlaceholder\":\"$PLACEHOLDER\"}]}}"
  if aws quicksight describe-template --aws-account-id "$AWS_ACCOUNT_ID" --template-id "$TEMPLATE_ID" --region "$REGION" >/dev/null 2>&1; then
    aws quicksight update-template --aws-account-id "$AWS_ACCOUNT_ID" --template-id "$TEMPLATE_ID" --name "$NAME" --source-entity "$SRC" --region "$REGION" >/dev/null
  else
    aws quicksight create-template \
      --aws-account-id "$AWS_ACCOUNT_ID" \
      --template-id "$TEMPLATE_ID" \
      --name "$NAME" \
      --permissions "[{\"Principal\":\"$QS_USER_ARN\",\"Actions\":[\"quicksight:DescribeTemplate\",\"quicksight:UpdateTemplate\",\"quicksight:DeleteTemplate\",\"quicksight:DescribeTemplatePermissions\"]}]" \
      --source-entity "$SRC" \
      --region "$REGION" >/dev/null
  fi
}

publish_dashboard_from_template () {
  local DASHBOARD_ID="$1"; local NAME="$2"; local TEMPLATE_ID="$3"; local DS_ARN="$4"; local PLACEHOLDER="$5"
  local TEMPLATE_ARN="arn:aws:quicksight:${REGION}:${AWS_ACCOUNT_ID}:template/${TEMPLATE_ID}"
  local SRC="{\"SourceTemplate\":{\"Arn\":\"$TEMPLATE_ARN\",\"DataSetReferences\":[{\"DataSetArn\":\"$DS_ARN\",\"DataSetPlaceholder\":\"$PLACEHOLDER\"}]}}"
  if aws quicksight describe-dashboard --aws-account-id "$AWS_ACCOUNT_ID" --dashboard-id "$DASHBOARD_ID" --region "$REGION" >/dev/null 2>&1; then
    aws quicksight update-dashboard --aws-account-id "$AWS_ACCOUNT_ID" --dashboard-id "$DASHBOARD_ID" --name "$NAME" --source-entity "$SRC" --region "$REGION" >/dev/null
  else
    aws quicksight create-dashboard \
      --aws-account-id "$AWS_ACCOUNT_ID" \
      --dashboard-id "$DASHBOARD_ID" \
      --name "$NAME" \
      --permissions "[{\"Principal\":\"$QS_USER_ARN\",\"Actions\":[\"quicksight:DescribeDashboard\",\"quicksight:ListDashboardVersions\",\"quicksight:QueryDashboard\",\"quicksight:UpdateDashboardPermissions\",\"quicksight:UpdateDashboard\",\"quicksight:DeleteDashboard\",\"quicksight:DescribeDashboardPermissions\",\"quicksight:UpdateDashboardPublishedVersion\"]}]" \
      --source-entity "$SRC" \
      --region "$REGION" >/dev/null
  fi
  local VER
  VER=$(aws quicksight describe-dashboard --aws-account-id "$AWS_ACCOUNT_ID" --dashboard-id "$DASHBOARD_ID" --query "Dashboard.Version.VersionNumber" --output text --region "$REGION")
  aws quicksight update-dashboard-published-version --aws-account-id "$AWS_ACCOUNT_ID" --dashboard-id "$DASHBOARD_ID" --version-number "$VER" --region "$REGION" >/dev/null || true
}

create_or_update_analysis "movies-analysis" "Movies Analysis" "$movies_def"
create_or_update_analysis "series-analysis" "Series Analysis" "$series_def"

create_or_update_template "movies-template" "Movies Template" "movies-analysis" "$MOVIES_DS_ARN" "movies_ds"
create_or_update_template "series-template" "Series Template" "series-analysis" "$SERIES_DS_ARN" "series_ds"

publish_dashboard_from_template "movies-dashboard" "Movies Dashboard" "movies-template" "$MOVIES_DS_ARN" "movies_ds"
publish_dashboard_from_template "series-dashboard" "Series Dashboard" "series-template" "$SERIES_DS_ARN" "series_ds"

rm -f "$movies_def" "$series_def"
echo "Done."
