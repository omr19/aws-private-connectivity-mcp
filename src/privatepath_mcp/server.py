import os
import time

import boto3
from botocore.exceptions import ClientError
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="AWS Private Connectivity MCP",
    host="127.0.0.1",
    port=8000,
    stateless_http=True,
    json_response=True,
)


def _get_stack_outputs(
    cloudformation_client,
    stack_name: str,
) -> dict[str, str]:
    response = cloudformation_client.describe_stacks(
        StackName=stack_name,
    )

    outputs = response["Stacks"][0].get("Outputs", [])

    return {
        output["OutputKey"]: output["OutputValue"]
        for output in outputs
    }


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


@mcp.tool()
def get_lab_resources() -> dict:
    """Return deployed resources and outputs for the PrivatePath lab."""
    session = boto3.Session()
    region = session.region_name or "eu-west-3"
    stack_name = os.getenv("PRIVATEPATH_STACK_NAME", "InfrastructureStack")

    cloudformation = session.client(
        "cloudformation",
        region_name=region,
    )

    stack_response = cloudformation.describe_stacks(
        StackName=stack_name,
    )

    resource_response = cloudformation.describe_stack_resources(
        StackName=stack_name,
    )

    stack = stack_response["Stacks"][0]

    return {
        "status": "ok",
        "region": region,
        "stack": stack_name,
        "stack_status": stack["StackStatus"],
        "outputs": stack.get("Outputs", []),
        "resources": [
            {
                "logical_id": resource["LogicalResourceId"],
                "type": resource["ResourceType"],
                "physical_id": resource["PhysicalResourceId"],
            }
            for resource in resource_response["StackResources"]
        ],
    }


@mcp.tool()
def diagnose_ec2_path() -> dict:
    """Analyze Application A to Application B connectivity on TCP 8080."""
    session = boto3.Session()
    region = session.region_name or "eu-west-3"
    stack_name = os.getenv("PRIVATEPATH_STACK_NAME", "InfrastructureStack")

    cloudformation = session.client(
        "cloudformation",
        region_name=region,
    )

    ec2 = session.client(
        "ec2",
        region_name=region,
    )

    outputs = _get_stack_outputs(
        cloudformation,
        stack_name,
    )

    source_instance = outputs["ApplicationAInstanceId"]
    destination_instance = outputs["ApplicationBInstanceId"]

    path_response = ec2.create_network_insights_path(
        Source=source_instance,
        Destination=destination_instance,
        Protocol="tcp",
        DestinationPort=8080,
        TagSpecifications=[
            {
                "ResourceType": "network-insights-path",
                "Tags": [
                    {
                        "Key": "Project",
                        "Value": "aws-private-connectivity-mcp",
                    },
                    {
                        "Key": "Purpose",
                        "Value": "MCP connectivity analysis",
                    },
                ],
            }
        ],
    )

    path_id = path_response["NetworkInsightsPath"]["NetworkInsightsPathId"]

    analysis_response = ec2.start_network_insights_analysis(
        NetworkInsightsPathId=path_id,
    )

    analysis_id = analysis_response["NetworkInsightsAnalysis"][
        "NetworkInsightsAnalysisId"
    ]

    status = "running"
    analysis = {}

    for _ in range(20):
        time.sleep(3)

        result = ec2.describe_network_insights_analyses(
            NetworkInsightsAnalysisIds=[analysis_id],
        )

        analysis = result["NetworkInsightsAnalyses"][0]
        status = analysis["Status"]

        if status in {"succeeded", "failed"}:
            break

    return {
        "status": status,
        "region": region,
        "source_instance": source_instance,
        "destination_instance": destination_instance,
        "destination_port": 8080,
        "network_insights_path_id": path_id,
        "network_insights_analysis_id": analysis_id,
        "network_path_found": analysis.get("NetworkPathFound"),
        "explanations": analysis.get("Explanations", []),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")