# Business Case and Evidence

## Business case

AWS private-connectivity failures are often caused by small differences between the intended path and the actual path: a security-group rule, an endpoint policy or state, a route-table association, or an IAM permission. Engineers typically gather evidence from several AWS consoles and CLI commands before explaining the root cause.

This project packages that investigation as a small MCP toolset. An MCP host such as Kiro can request a focused diagnostic, receive normalized AWS evidence, and present an explanation and safe remediation suggestion. The server does not make changes automatically.

## What has been accomplished

- Created the private GitHub repository `omr19/aws-private-connectivity-mcp`.
- Established the local project layout, Python 3.12 virtual environment, and development dependencies.
- Configured and verified the `your-sandbox-profile` AWS identity for `eu-west-3`.
- Built the first FastMCP server from scratch using Streamable HTTP.
- Added the `get_lab_topology` tool.
- Started the server at `http://127.0.0.1:8000/mcp`.
- Connected MCP Inspector as a client and observed protocol requests such as `tools/list`.
- Executed `get_lab_topology` through Inspector and verified the structured response.
- Built and ran a direct Python MCP client against the same Streamable HTTP endpoint.
- Registered the server in Kiro Workspace MCP configuration with manual tool approval enabled.
- Invoked the tool successfully from Kiro and received the same structured topology response.
- Added and invoked `get_aws_identity`, confirming a real boto3 call through the `your-sandbox-profile` assumed role in `eu-west-3`.
- Created and reviewed the CDK stack for the healthy lab, including project tags, two isolated subnets, EC2 applications, S3 gateway endpoint, and Secrets Manager interface endpoint.
- Bootstrapped the CDK environment in `eu-west-3`; the application stack remains intentionally undeployed at this checkpoint.

The current response is deliberately marked `status: mock`. This proves the MCP flow across three clients before AWS resources, permissions, and failure scenarios are introduced.

The identity tool is the first non-mock AWS integration. It confirms that the server process uses its own exported AWS profile and region, which is why the initial default-profile result differed from the final assumed-role result.

## Phase 1 evidence and screenshot plan

Screenshots should be copied into `docs/screenshots/` using the names below. The temporary screenshots shared in chat are the source evidence; do not commit browser tokens or credentials visible in URLs.

| File | Phase evidence |
| --- | --- |
| `01-environment-and-repository.png` | Local repo, Kiro project, and environment setup |
| `02-fastmcp-server-running.png` | FastMCP server listening on `127.0.0.1:8000` |
| `03-inspector-connected.png` | `privatepath-local` connected over Streamable HTTP |
| `04-tools-list.png` | Inspector discovers `get_lab_topology` |
| `05-tool-result.png` | Tool execution returns topology JSON |

Expected layout:

```text
docs/screenshots/
  01-environment-and-repository.png
  02-fastmcp-server-running.png
  03-inspector-connected.png
  04-tools-list.png
  05-tool-result.png
```

## Intended production-shaped use case

The target lab will model Application A reaching Application B over TCP 8080, Secrets Manager through an interface VPC endpoint, and S3 through a gateway VPC endpoint. MCP tools will report evidence, likely root cause, and proposed remediation for one controlled fault at a time. They will not mutate networking or IAM configuration.

## Success criteria

- Explain Host, Client, Server, Tool, and transport roles.
- Invoke the same tool locally through Inspector, a direct client, and Kiro.
- Distinguish network reachability from IAM authorization.
- Reprovision and remove the lab safely with IaC.
- Store no credentials, Inspector tokens, or production data in Git.
