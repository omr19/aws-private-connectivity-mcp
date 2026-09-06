# Resume bullets

- Built a FastMCP server from scratch using Streamable HTTP, exposing AWS private-connectivity diagnostics to MCP Inspector, a Python client, and Kiro.
- Provisioned a tagged AWS private-network lab in eu-west-3 with AWS CDK: isolated VPC subnets, EC2 workloads, a Secrets Manager interface VPC endpoint, and an S3 gateway endpoint.
- Integrated boto3 with CloudFormation, EC2, STS, VPC endpoints, and Reachability Analyzer to return normalized network evidence through MCP tools.
- Diagnosed and remediated controlled EC2 and interface-endpoint failures by identifying ENI_SG_RULES_MISMATCH and restoring least-scope security-group rules.
- Implemented reproducible IaC, IAM troubleshooting, evidence screenshots, and cost-conscious teardown controls for a portfolio-ready AWS networking lab.

## Evidence

See docs/screenshots/, docs/business-case.md, and the develop branch history.
