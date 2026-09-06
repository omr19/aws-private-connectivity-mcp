# LinkedIn project summary

Built a compact AWS private-connectivity lab to learn and demonstrate the full Model Context Protocol flow: MCP host, client, server, tools, and Streamable HTTP transport.

The project uses a FastMCP server and AWS CDK to model two isolated EC2 applications, a Secrets Manager interface VPC endpoint, and an S3 gateway endpoint. MCP tools call AWS APIs to return identity, deployed-resource inventory, Reachability Analyzer evidence, interface-endpoint diagnosis, and gateway-route inspection.

The strongest learning outcome was turning a deliberately broken security-group path into an explainable troubleshooting workflow. Reachability Analyzer identified the ingress mismatch, Kiro presented the normalized evidence, and the rule was restored manually and verified. The lab is intentionally small, reproducible, tagged, and designed for safe teardown.
