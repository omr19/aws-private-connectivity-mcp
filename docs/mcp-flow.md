# MCP flow learning notes

Complete this document during the lab using observations from the direct client, MCP Inspector, Kiro, and AgentCore logs.

## Components

- Host:
- Client:
- Server:
- Tool:
- Transport:
- External service:

## Local request trace

Document the observed sequence from connection through tool result.

## Remote request trace

Document what changes after deployment to AgentCore Runtime.

## MCP versus AWS responsibilities

| Concern | Owner |
| --- | --- |
| Tool discovery | MCP |
| Tool selection | Host/model |
| AWS API request | Tool implementation and AWS SDK |
| AWS authorization | IAM |
| Server compute | AgentCore Runtime |

