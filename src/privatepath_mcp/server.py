import boto3

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="AWS Private Connectivity MCP",
    host="127.0.0.1",
    port=8000,
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def get_lab_topology() -> dict:
    """Return the initial topology for the PrivatePath learning lab."""
    return {
        "project": "aws-private-connectivity-mcp",
        "region": "eu-west-3",
        "status": "mock",
        "paths": [
            "application-a -> application-b:8080",
            "application-a -> Secrets Manager interface endpoint:443",
            "application-a -> S3 gateway endpoint",
        ],
        "message": "This is the first mock MCP tool. AWS integration comes later.",
    }


@mcp.tool()
def get_aws_identity() -> dict:
    """Return the AWS identity and region used by this MCP server."""
    session = boto3.Session()
    region = session.region_name or "eu-west-3"

    sts = session.client("sts", region_name=region)
    identity = sts.get_caller_identity()

    return {
        "status": "ok",
        "region": region,
        "account": identity["Account"],
        "arn": identity["Arn"],
        "user_id": identity["UserId"],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")