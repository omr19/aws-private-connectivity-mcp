# Portfolio audit

## Current status

- [x] Local FastMCP server runs over Streamable HTTP.
- [x] Direct client, MCP Inspector, and Kiro invoke the same server.
- [x] CDK infrastructure is deployed and tagged in eu-west-3.
- [x] EC2 healthy, blocked, and remediated paths are evidenced.
- [x] Secrets Manager interface endpoint healthy, blocked, and remediated paths are evidenced.
- [x] S3 gateway endpoint route-table inspection is evidenced.
- [x] Screenshots 01–11 are stored under docs/screenshots/.
- [x] Environment-specific CDK outputs are excluded from Git.
- [ ] Merge the reviewed develop branch into main when the portfolio gate is approved.
- [ ] Destroy the AWS lab after the final demonstration.

## Security and cost notes

- No credentials, secret values, or Inspector tokens are committed.
- The MCP server does not mutate networking or IAM configuration.
- Reachability Analyzer analyses incur usage charges; avoid repeated unnecessary runs.
- EC2, interface endpoints, Secrets Manager, and other lab resources continue to incur charges until the CDK stack is destroyed.
- The CDK stack uses learning-lab tags and destructive removal policies for controlled teardown.

## Final review

Before publicizing the project, review README accuracy, confirm GitHub repository visibility, run the end-to-end demo once, and destroy or explicitly retain AWS resources.
