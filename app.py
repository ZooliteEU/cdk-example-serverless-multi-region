#!/usr/bin/env python3

from aws_cdk import core

from serverless_multi_region.serverless_multi_region_stack import ServerlessMultiRegionStack


app = core.App()

env_EU = core.Environment(account="123456789012", region="eu-west-1")
env_US = core.Environment(account="123456789012", region="us-east-1")

ServerlessMultiRegionStack(
    app,
    "serverless-multi-region-eu",
    cert_arn="arn:aws:acm:eu-west-1:123456789012:certificate/6c626c29-7573-44bc-b458-efd989e0070a",
    env=env_EU,
)

ServerlessMultiRegionStack(
    app,
    "serverless-multi-region-us",
    cert_arn="arn:aws:acm:us-east-1:123456789012:certificate/551e8c57-e6e1-45e7-bf01-bb2fcc19fd23",
    env=env_US,
)

app.synth()
