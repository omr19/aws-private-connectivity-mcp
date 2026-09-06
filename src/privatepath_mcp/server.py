import os
import time

import boto3
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


def _run_network_analysis(
    ec2_client,
    source: str,
    destination: str,
    destination_port: int,
    purpose: str,
) -> dict:
    path_response = ec2_client.create_network_insights_path(
        Source=source,
        Destination=destination,
        Protocol="tcp",
        DestinationPort=destination_port,
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
                        "Value": purpose,
                    },
                ],
            }
        ],
    )

    path_id = path_response["NetworkInsightsPath"]["NetworkInsightsPathId"]

    analysis_response = ec2_client.start_network_insights_analysis(
        NetworkInsightsPathId=path_id,
    )

    analysis_id = analysis_response["NetworkInsightsAnalysis"][
        "NetworkInsightsAnalysisId"
    ]

    status = "running"
    analysis = {}

    for _ in range(20):
        time.sleep(3)

        result = ec2_client.describe_network_insights_analyses(
            NetworkInsightsAnalysisIds=[analysis_id],
        )

        analysis = result["NetworkInsightsAnalyses"][0]
        status = analysis["Status"]

        if status in {"succeeded", "failed"}:
            break

    return {
        "status": status,
        "network_insights_path_id": path_id,
        "network_insights_analysis_id": analysis_id,
        "network_path_found": analysis.get("NetworkPathFound"),
        "explanations": analysis.get("Explanations", []),
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

    analysis = _run_network_analysis(
        ec2_client=ec2,
        source=source_instance,
        destination=destination_instance,
        destination_port=8080,
        purpose="MCP EC2 connectivity analysis",
    )

    return {
        "status": analysis["status"],
        "region": region,
        "source_instance": source_instance,
        "destination_instance": destination_instance,
        "destination_port": 8080,
        "network_insights_path_id": analysis[
            "network_insights_path_id"
        ],
        "network_insights_analysis_id": analysis[
            "network_insights_analysis_id"
        ],
        "network_path_found": analysis["network_path_found"],
        "explanations": analysis["explanations"],
    }


@mcp.tool()
def diagnose_secrets_endpoint() -> dict:
    """Analyze Application A to the Secrets Manager interface endpoint on TCP 443."""
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
    vpc_id = outputs["VpcId"]

    endpoint_response = ec2.describe_vpc_endpoints(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id],
            },
            {
                "Name": "service-name",
                "Values": [
                    f"com.amazonaws.{region}.secretsmanager",
                ],
            },
        ],
    )

    endpoints = endpoint_response["VpcEndpoints"]

    if not endpoints:
        return {
            "status": "not_found",
            "region": region,
            "source_instance": source_instance,
            "message": "Secrets Manager interface endpoint was not found.",
        }

    endpoint = endpoints[0]
    endpoint_id = endpoint["VpcEndpointId"]
    destination_eni = endpoint["NetworkInterfaceIds"][0]

    analysis = _run_network_analysis(
        ec2_client=ec2,
        source=source_instance,
        destination=destination_eni,
        destination_port=443,
        purpose="MCP Secrets Manager endpoint analysis",
    )

    return {
        "status": analysis["status"],
        "region": region,
        "source_instance": source_instance,
        "destination_network_interface": destination_eni,
        "vpc_endpoint_id": endpoint_id,
        "destination_port": 443,
        "network_insights_path_id": analysis[
            "network_insights_path_id"
        ],
        "network_insights_analysis_id": analysis[
            "network_insights_analysis_id"
        ],
        "network_path_found": analysis["network_path_found"],
        "explanations": analysis["explanations"],
    }


@mcp.tool()
def inspect_s3_gateway_endpoint() -> dict:
    """Inspect the S3 gateway endpoint and its route-table associations."""
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

    vpc_id = outputs["VpcId"]

    endpoint_response = ec2.describe_vpc_endpoints(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id],
            },
            {
                "Name": "service-name",
                "Values": [
                    f"com.amazonaws.{region}.s3",
                ],
            },
            {
                "Name": "vpc-endpoint-type",
                "Values": ["Gateway"],
            },
        ],
    )

    endpoints = endpoint_response["VpcEndpoints"]

    if not endpoints:
        return {
            "status": "not_found",
            "region": region,
            "vpc_id": vpc_id,
            "message": "S3 gateway endpoint was not found.",
        }

    endpoint = endpoints[0]
    route_table_ids = endpoint.get("RouteTableIds", [])
    route_tables = []

    if route_table_ids:
        route_response = ec2.describe_route_tables(
            RouteTableIds=route_table_ids,
        )

        for route_table in route_response["RouteTables"]:
            prefix_list_routes = [
                route
                for route in route_table.get("Routes", [])
                if route.get("PrefixListId")
            ]

            route_tables.append(
                {
                    "route_table_id": route_table["RouteTableId"],
                    "prefix_list_routes": prefix_list_routes,
                }
            )

    return {
        "status": "ok",
        "region": region,
        "vpc_id": vpc_id,
        "vpc_endpoint_id": endpoint["VpcEndpointId"],
        "endpoint_type": endpoint["VpcEndpointType"],
        "endpoint_state": endpoint["State"],
        "service_name": endpoint["ServiceName"],
        "route_table_ids": route_table_ids,
        "route_tables": route_tables,
        "message": (
            "S3 gateway endpoint routing is present through route tables."
            if route_tables
            else "S3 gateway endpoint has no associated route tables."
        ),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")