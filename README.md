# AWS Private Connectivity MCP

A deliberately small, hands-on project for learning the Model Context Protocol (MCP) end to end while diagnosing fixed AWS private-connectivity scenarios.

The project will be built manually in Kiro and deployed to Amazon Bedrock AgentCore Runtime in `eu-west-3`. Infrastructure will be reproducible with AWS CDK for Python.

## Primary learning objective

Build enough of every layer to explain this flow clearly:

```text
User
  -> Kiro host
  -> MCP client
  -> FastMCP server on AgentCore Runtime
  -> AWS SDK
  -> AWS networking and IAM evidence
  -> structured MCP result
  -> model explanation
```

MCP Inspector and a small Python client will be used before Kiro so the protocol remains visible.

## Fixed lab scope

```text
EC2 Application A
  |-- TCP 8080 --> EC2 Application B
  |-- HTTPS ----> Secrets Manager interface endpoint
  `-- HTTPS ----> S3 gateway endpoint --> private test bucket
```

No ALB or NLB is required. The interface endpoint connects to the AWS-managed Secrets Manager service. The gateway endpoint connects the VPC to S3 through a route-table association.

### Supported diagnostic scenarios

1. Application B is missing inbound TCP 8080 from Application A.
2. The Secrets Manager interface endpoint is missing inbound TCP 443 from Application A.
3. The S3 gateway endpoint is not associated with Application A's route table.
4. Optional if time permits: Application A lacks `s3:GetObject`.

Only one fault will be enabled at a time. The MCP server will recommend remediation but will not change AWS networking or IAM configuration.

## Implemented MCP tools

| Tool | Purpose |
| --- | --- |
| `get_lab_topology` | Return the known lab resources and expected paths. |
| `diagnose_ec2_path` | Run and normalize an EC2-to-EC2 Reachability Analyzer result. |
| `diagnose_secrets_endpoint` | Run and normalize Application A to the Secrets Manager interface endpoint on TCP 443. |
| `inspect_s3_gateway_endpoint` | Inspect the S3 gateway endpoint state and route-table associations. |

## Learning sequence

Each phase has a working checkpoint. Do not continue until the checkpoint can be explained without relying on generated summaries.

### Phase 1 — Local FastMCP server (completed)

- Implement one mock `get_lab_topology` tool.
- Run the server locally.
- Discover and invoke it with MCP Inspector.
- Observe a validation error.

Checkpoint: explain `tools/list`, `tools/call`, schemas, and structured results. **Completed:** the server was started locally on `127.0.0.1:8000`, connected through MCP Inspector, and `get_lab_topology` returned structured JSON.

### Phase 2 — Direct MCP client and Kiro

- Build a minimal Python MCP client.
- List and invoke tools without a model.
- Register the local server in Kiro.
- Keep tool auto-approval disabled.

Checkpoint: invoke the same server from the direct client, MCP Inspector, and Kiro. **Completed:** all three clients discovered and invoked `get_lab_topology` successfully.

### Phase 3 — Healthy AWS lab

Before provisioning the lab, the first AWS-backed checkpoint is complete: `get_aws_identity` successfully called AWS STS through boto3 and confirmed the `your-sandbox-profile` assumed role in `eu-west-3`.

- Provision one VPC, two private subnets, and two small EC2 applications.
- Add one Secrets Manager interface endpoint.
- Add one S3 gateway endpoint and harmless test object.
- Verify all three paths before injecting faults.

Checkpoint: prove the lab is healthy independently of MCP.

### Phase 4 — AWS-backed MCP tools

- Replace mock results with narrowly scoped AWS SDK calls.
- Use Reachability Analyzer for the EC2 path.
- Return evidence, root cause, and proposed remediation.

Checkpoint: every tool reports `PASS` against the healthy lab.

### Phase 5 — AgentCore deployment

- Package and deploy the FastMCP server to AgentCore Runtime.
- Assign least-privilege AWS permissions.
- Connect the direct client, Inspector, and Kiro to the remote endpoint.

Checkpoint: the same tools work locally and remotely.

### Phase 6 — Controlled troubleshooting

- Inject one fault at a time.
- Diagnose it through Kiro.
- Compare the model explanation with raw MCP evidence.
- Restore the healthy state after every scenario.

Checkpoint: distinguish security-group, endpoint, route, and IAM failures.

### Phase 7 — Document and remove

- Capture the architecture and MCP sequence.
- Record expected results and limitations.
- Destroy all AWS resources and confirm cleanup.

## Repository structure

```text
src/privatepath_mcp/     FastMCP server and tools
client/                  Direct protocol client
infrastructure/          AWS CDK application and stacks
tests/                   Unit tests with mocked AWS responses
docs/                    Architecture, MCP flow, and scenarios
.kiro/settings/          Safe example MCP configuration only
```

Directories will be populated progressively during the lab rather than generated as a finished solution upfront.

## Guardrails

- Region is fixed to `eu-west-3`.
- Use a sandbox AWS account or tightly scoped lab role.
- Never commit credentials, tokens, secrets, or a live Kiro MCP configuration.
- Keep Kiro MCP `autoApprove` empty during learning.
- No automatic remediation.
- No multi-region, cross-account, Transit Gateway, peering, NAT, load balancer, database, RAG, dashboard, or multi-agent features.
- The harmless Secrets Manager value and S3 object must contain no production data.
- Destroy the interface endpoint, EC2 instances, and AgentCore resources after the exercise.

## Prerequisites

- Python 3.12+
- Node.js and npm for MCP Inspector and AgentCore tooling
- AWS CLI authenticated to a sandbox account
- AWS CDK CLI
- Kiro IDE or CLI with MCP enabled
- Access to EC2, VPC, S3, Secrets Manager, IAM, Reachability Analyzer, CloudFormation, and AgentCore in `eu-west-3`

## Status

Phases 1 and 2 completed in Kiro. The first AWS-backed identity check is working, and the CDK infrastructure stack has synthesized and passed review with no deployment yet. The returned topology is intentionally marked `mock`; the healthy AWS lab is the next deployment checkpoint.

See [Business Case and Evidence](docs/business-case.md) for the project rationale, accomplishments, and screenshot/evidence plan.
