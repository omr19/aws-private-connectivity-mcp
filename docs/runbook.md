# Reproduction and teardown runbook

This runbook reproduces the AWS Private Connectivity MCP lab in eu-west-3 and removes the application resources after the demonstration.

## 1. Prerequisites

- AWS CLI configured with the `your-sandbox-profile` profile.
- Python 3.12 and Node.js installed.
- Access to the private GitHub repository.
- Permissions for CDK bootstrap, CloudFormation, EC2, VPC endpoints, IAM, S3, Secrets Manager, and Reachability Analyzer.

From the repository root:

```bash
cd /Users/rizwansharif/Documents/Codex/aws-private-connectivity-mcp
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
export AWS_PROFILE=your-sandbox-profile
export AWS_REGION=eu-west-3
export AWS_DEFAULT_REGION=eu-west-3
aws sts get-caller-identity
```

## 2. Bootstrap CDK once per account and region

From the `infrastructure/` directory:

```bash
cd infrastructure
source .venv/bin/activate
npx aws-cdk bootstrap aws://<ACCOUNT_ID>/eu-west-3
```

Bootstrap is an account/region prerequisite. It may remain after the application stack is destroyed; remove it only when it is no longer used by any CDK project. CloudFormation itself has no additional charge for AWS-native resources, but the resources represented by the application stack are billed normally. Leaving the stack record does not make EC2 instances, interface endpoints, Secrets Manager, or other resources free. Keeping the CDK bootstrap stack can make future reproduction easier, but keeping the application stack deployed should be treated as an active-cost decision.

## 3. Synthesize and deploy

```bash
npx aws-cdk synth
npx aws-cdk diff
npx aws-cdk deploy --require-approval broadening --outputs-file cdk-outputs.json
```

Record the CloudFormation outputs. The stack creates the tagged VPC, two isolated-subnet EC2 instances, an S3 gateway endpoint, a Secrets Manager interface endpoint, a private bucket, and a private secret.

## 4. Run the local MCP server

Open a project-root terminal and keep it running:

```bash
cd /Users/rizwansharif/Documents/Codex/aws-private-connectivity-mcp
source .venv/bin/activate
export AWS_PROFILE=your-sandbox-profile
export AWS_REGION=eu-west-3
export AWS_DEFAULT_REGION=eu-west-3
python -m py_compile src/privatepath_mcp/server.py
PYTHONPATH=src python -m privatepath_mcp.server
```

The endpoint is `http://127.0.0.1:8000/mcp`.

## 5. Connect clients

- MCP Inspector: run `npx @modelcontextprotocol/inspector`, add the Streamable HTTP URL, and connect.
- Direct client: run `python client/test_client.py` from the root virtual environment.
- Kiro: configure `.kiro/settings/mcp.json`, reload the window, and approve tools manually.

## 6. Validate the healthy lab

Run these tools through Kiro or Inspector:

- `get_aws_identity`
- `get_lab_resources`
- `diagnose_ec2_path`
- `diagnose_secrets_endpoint`
- `inspect_s3_gateway_endpoint`

Expected healthy results include `network_path_found: true` for the EC2 and Secrets Manager paths and an `Available` S3 gateway endpoint with associated route tables.

## 7. Controlled troubleshooting scenarios

Use the AWS infrastructure terminal, never the MCP server terminal.

EC2 rule: revoke and restore the Application A to Application B TCP 8080 ingress rule.

Secrets endpoint rule: revoke and restore Application A to the endpoint security group on TCP 443.

After each change, run the matching MCP diagnostic, capture evidence, and restore the rule immediately. Do not leave the lab in a failed state.

## 8. Teardown checklist

Run from `infrastructure/`:

```bash
export AWS_PROFILE=your-sandbox-profile
export AWS_REGION=eu-west-3
export AWS_DEFAULT_REGION=eu-west-3
npx aws-cdk destroy --force
```

Then verify no application resources remain:

```bash
aws cloudformation describe-stacks --stack-name InfrastructureStack --region eu-west-3
aws ec2 describe-instances --filters Name=tag:Project,Values=aws-private-connectivity-mcp --region eu-west-3
aws ec2 describe-vpc-endpoints --filters Name=tag:Project,Values=aws-private-connectivity-mcp --region eu-west-3
aws s3api list-buckets --query 'Buckets[?starts_with(Name, `infrastructurestack-privatetestbucket`)].Name'
aws secretsmanager list-secrets --filters Key=name,Values=aws-private-connectivity-mcp/lab-secret --region eu-west-3
```

The expected result is that the application stack is absent, no tagged EC2 instances or VPC endpoints remain, the lab bucket is absent, and the lab secret is absent. Also check the AWS console for CloudFormation, EC2, VPC endpoints, S3, Secrets Manager, and Reachability Analyzer analyses.

Do not delete the CDK bootstrap stack automatically if the account uses it for other projects. Remove old Network Insights paths and analyses if they are still visible and no longer needed.

## 9. Git safety

Do not commit `.env`, AWS credentials, Inspector tokens, secret values, or environment-specific `infrastructure/cdk-outputs.json`.
