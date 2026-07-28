# Planned Terraform modules

The following module boundaries are reserved: `api_gateway`, `bedrock`, `cockroachdb`,
`eventbridge`, `iam`, `kms`, `lambda`, `monitoring`, `network`, `s3`, `sns`, `sqs`, and
`step_functions`. Each module will expose explicit variables and outputs, use
least-privilege IAM, and contain no environment-specific values.
