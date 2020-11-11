from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_logs,
    aws_apigateway as apigateway,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as certificatemanager
)
import os


class ServerlessMultiRegionStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, cert_arn, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # -- Lambda function
        my_function = _lambda.Function(
            self,
            "MyFunction",
            code=_lambda.Code.from_asset("dist"),
            handler="myfunction",
            runtime=_lambda.Runtime.GO_1_X,
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            memory_size=128,
            events=[],
        )

        # -- API Gateway
        my_api = apigateway.RestApi(
            self,
            "MyApi"
        )

        myfunction_integration = apigateway.LambdaIntegration(my_function)

        test_resource = my_api.root.add_resource("test")
        test_resource.add_method("GET", myfunction_integration)

        # -- DNS Configuration
        # Get the Route53 Zone
        dns_zone = route53.HostedZone.from_lookup(
            self,
            "ApiZone",
            private_zone=False,
            domain_name="zoolite.eu"
        )

        # Get the certificate
        api_domain_cert = certificatemanager.Certificate.from_certificate_arn(
            self,
            "DomainCertificate",
            cert_arn
        )

        # Create the Custom Domain
        api_dns_name = apigateway.DomainName(
            self,
            "ApiDomainName",
            domain_name="my-api.zoolite.eu",
            endpoint_type=apigateway.EndpointType.REGIONAL,
            certificate=api_domain_cert,
            security_policy=apigateway.SecurityPolicy.TLS_1_2
        )

        #api_dns_name.add_base_path_mapping(my_api, base_path="test")
        api_dns_name.add_base_path_mapping(my_api)

        # Create the Route53 record
        api_dns_record = route53.ARecord(
            self,
            "MyAPiDNSRecord",
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(api_dns_name)
            ),
            record_name="my-api",
            zone=dns_zone
        )

        # Configure latency based routing on record
        recordset = api_dns_record.node.default_child
        recordset.region = self.region
        recordset.set_identifier = api_dns_record.node.unique_id
