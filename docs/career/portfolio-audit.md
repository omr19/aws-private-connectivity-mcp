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
- [ ] Decide whether to retain the application stack for a short follow-up demo; CloudFormation has no additional charge, but deployed EC2 and interface-endpoint resources continue to incur normal charges.
- [ ] If the lab is no longer needed, run the teardown and verify every application resource is gone.
- [ ] Retain the CDK bootstrap stack only if it supports future CDK reproduction; it is separate from the application stack.

## Security and cost notes

- No credentials, secret values, or Inspector tokens are committed.
- The MCP server does not mutate networking or IAM configuration.
- Reachability Analyzer analyses incur usage charges; avoid repeated unnecessary runs.
- EC2, interface endpoints, Secrets Manager, and other lab resources continue to incur charges until the CDK stack is destroyed.
- The CDK stack uses learning-lab tags and destructive removal policies for controlled teardown.

## Teardown checklist

- [ ] Run `npx aws-cdk destroy --force` from `infrastructure/`.
- [ ] Confirm `InfrastructureStack` is absent from CloudFormation.
- [ ] Confirm no project-tagged EC2 instances or VPC endpoints remain.
- [ ] Confirm the lab S3 bucket and Secrets Manager secret are removed.
- [ ] Confirm no leftover Reachability Analyzer paths or analyses require cleanup.
- [ ] Check the AWS console and cost view after teardown.
- [ ] Preserve the CDK bootstrap stack only if another project still uses it.

See `docs/runbook.md` for the complete reproduction and teardown procedure.

## Final review

Before publicizing the project, review README accuracy, confirm GitHub repository visibility, run the end-to-end demo once, and destroy or explicitly retain AWS resources.
