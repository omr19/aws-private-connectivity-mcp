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
- [x] Keep the CDK source and synthesized template as the reusable IaC record; do not redeploy while the current lab is already running.
- [x] Run the teardown and verify every application resource is gone.
- [x] Retain the CDK bootstrap stack for future CDK reproduction; it is separate from the application stack.
- [x] Replace account-specific role/profile names and account IDs in public text with placeholders.
- [x] Replace screenshots containing AWS identifiers or local usernames with sanitized public evidence cards.
- [x] Scan tracked files and reachable Git history for credential patterns; none found.

## Security and cost notes

- No credentials, secret values, or Inspector tokens are committed.
- Public evidence cards redact account IDs, ARNs, resource IDs, role/profile names, local usernames, and filesystem paths.
- The original private captures are retained outside the repository for audit/reference only.
- The MCP server does not mutate networking or IAM configuration.
- Reachability Analyzer analyses incur usage charges; avoid repeated unnecessary runs.
- EC2, interface endpoints, Secrets Manager, and other lab resources continue to incur charges until the CDK stack is destroyed.
- The CDK stack uses learning-lab tags and destructive removal policies for controlled teardown.

## Teardown checklist

- [x] Run `npx aws-cdk destroy --force` from `infrastructure/`.
- [x] Confirm `InfrastructureStack` is absent from CloudFormation.
- [x] Confirm no project-tagged EC2 instances or VPC endpoints remain.
- [x] Confirm the lab S3 bucket and Secrets Manager secret are removed.
- [x] Confirm no leftover Reachability Analyzer paths or analyses require cleanup.
- [x] Check the AWS console and cost view after teardown.
- [x] Preserve the CDK bootstrap stack for future reproduction.

See `docs/runbook.md` for the complete reproduction and teardown procedure.

## Final review

Before publicizing the project, review README accuracy, confirm GitHub repository visibility, run the end-to-end demo once, verify GitHub secret scanning, and destroy or explicitly retain AWS resources.
