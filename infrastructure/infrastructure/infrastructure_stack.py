from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    Tags,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class InfrastructureStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add("Project", "aws-private-connectivity-mcp")
        Tags.of(self).add("Environment", "learning")
        Tags.of(self).add("ManagedBy", "AWS-CDK")
        Tags.of(self).add("Owner", "omr19")
        Tags.of(self).add("Purpose", "MCP private connectivity lab")
        Tags.of(self).add("DataClassification", "NonProduction")
        Tags.of(self).add("CostControl", "destroy-after-lab")

        vpc = ec2.Vpc(
            self,
            "LabVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                )
            ],
        )

        app_a_sg = ec2.SecurityGroup(
            self,
            "ApplicationASecurityGroup",
            vpc=vpc,
            description="Security group for Application A",
        )

        app_b_sg = ec2.SecurityGroup(
            self,
            "ApplicationBSecurityGroup",
            vpc=vpc,
            description="Security group for Application B",
        )

        endpoint_sg = ec2.SecurityGroup(
            self,
            "SecretsEndpointSecurityGroup",
            vpc=vpc,
            description="Security group for the Secrets Manager interface endpoint",
        )

        app_b_sg.add_ingress_rule(
            app_a_sg,
            ec2.Port.tcp(8080),
            "Allow Application A to reach Application B",
        )

        endpoint_sg.add_ingress_rule(
            app_a_sg,
            ec2.Port.tcp(443),
            "Allow Application A to reach Secrets Manager endpoint",
        )

        bucket = s3.Bucket(
            self,
            "PrivateTestBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        secret = secretsmanager.Secret(
            self,
            "PrivateTestSecret",
            description="Harmless learning-lab secret",
            secret_name="aws-private-connectivity-mcp/lab-secret",
            removal_policy=RemovalPolicy.DESTROY,
        )

        app_role = iam.Role(
            self,
            "ApplicationARole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="Learning-lab role for Application A",
        )

        bucket.grant_read(app_role)
        secret.grant_read(app_role)

        vpc.add_gateway_endpoint(
            "S3GatewayEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[
                ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                )
            ],
        )

        vpc.add_interface_endpoint(
            "SecretsManagerInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            open=False,
            subnets=ec2.SubnetSelection(
                subnets=[vpc.isolated_subnets[0]],
            ),
        )

        machine_image = ec2.MachineImage.latest_amazon_linux2023()

        app_a = ec2.Instance(
            self,
            "ApplicationA",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[vpc.isolated_subnets[0]],
            ),
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=machine_image,
            security_group=app_a_sg,
            role=app_role,
        )

        app_b = ec2.Instance(
            self,
            "ApplicationB",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[vpc.isolated_subnets[1]],
            ),
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=machine_image,
            security_group=app_b_sg,
        )

        CfnOutput(self, "VpcId", value=vpc.vpc_id)
        CfnOutput(self, "ApplicationAInstanceId", value=app_a.instance_id)
        CfnOutput(self, "ApplicationBInstanceId", value=app_b.instance_id)
        CfnOutput(self, "PrivateBucketName", value=bucket.bucket_name)
        CfnOutput(self, "PrivateSecretArn", value=secret.secret_arn)