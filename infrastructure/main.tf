locals {
  name = "rockpaperscissors"
}

locals {
  common_tags = {
    department = "bots"
    name       = local.name
    platform   = "twitter"
  }
}

data "external" "lambda" {
  working_dir = "${path.root}/../"
  program     = ["make", "--always-make", "function.zip"]
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "rockpaperscissors" {
  description = "${local.name} parameter store key"
  tags        = local.common_tags
}

data "aws_iam_policy_document" "lambda" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ssm" {
  statement {
    actions = [
      "ssm:GetParameter",
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.name}-*"
    ]
  }
  statement {
    actions = [
      "kms:Decrypt",
    ]
    resources = [
      aws_kms_key.rockpaperscissors.arn
    ]
  }
}

resource "aws_iam_policy" "ssm" {
  name   = "${local.name}-ssm"
  policy = data.aws_iam_policy_document.ssm.json
}

resource "aws_iam_role" "rockpaperscissors" {
  name               = local.name
  assume_role_policy = data.aws_iam_policy_document.lambda.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.rockpaperscissors.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.rockpaperscissors.name
  policy_arn = aws_iam_policy.ssm.arn
}

resource "aws_lambda_function" "rockpaperscissors" {
  description      = "Play rock paper scissors on Twitter"
  filename         = data.external.lambda.result.path
  function_name    = local.name
  handler          = "main.lambda_handler"
  role             = aws_iam_role.rockpaperscissors.arn
  timeout          = 15
  source_code_hash = filebase64sha256(data.external.lambda.result.path)
  runtime          = "python3.8"
  tags             = local.common_tags
}

resource "aws_ssm_parameter" "rockpaperscissors_api_key" {
  name   = "${local.name}-api-key"
  type   = "SecureString"
  value  = var.api_key
  key_id = aws_kms_key.rockpaperscissors.key_id
  tags   = local.common_tags
}

resource "aws_ssm_parameter" "rockpaperscissors_api_secret" {
  name   = "${local.name}-api-secret"
  type   = "SecureString"
  value  = var.api_secret
  key_id = aws_kms_key.rockpaperscissors.key_id
  tags   = local.common_tags
}

resource "aws_ssm_parameter" "rockpaperscissors_access_token" {
  name   = "${local.name}-access-token"
  type   = "SecureString"
  value  = var.access_token
  key_id = aws_kms_key.rockpaperscissors.key_id
  tags   = local.common_tags
}

resource "aws_ssm_parameter" "rockpaperscissors_access_token_secret" {
  name   = "${local.name}-access-token-secret"
  type   = "SecureString"
  value  = var.access_token_secret
  key_id = aws_kms_key.rockpaperscissors.key_id
  tags   = local.common_tags
}

resource "aws_cloudwatch_event_rule" "every_n_minutes" {
  name                = "every-n-minutes"
  description         = "Fires every n minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "rockpaperscissors" {
  rule      = aws_cloudwatch_event_rule.every_n_minutes.name
  target_id = local.name
  arn       = aws_lambda_function.rockpaperscissors.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rockpaperscissors.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_n_minutes.arn
}

resource "aws_budgets_budget" "rockpaperscissors" {
  name              = local.name
  budget_type       = "COST"
  limit_amount      = "1.0"
  limit_unit        = "USD"
  time_period_start = "2020-02-01_00:00"
  time_unit         = "MONTHLY"

  cost_filters = {
    Service     = "Lambda"
    TagKeyValue = replace("user:Name$X", "X", local.name)
  }
}
