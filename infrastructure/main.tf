locals {
  name           = "rockpaperscissors"
  lambda_package = "${path.root}/../lambda.zip"
}

locals {
  common_tags = {
    department = "bots"
    name       = local.name
    platform   = "twitter"
  }
}

data "aws_iam_policy_document" "lambda_policy" {
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

resource "aws_iam_role" "rockpaperscissors" {
  name               = "${local.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_policy.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "logging_policy" {
  role       = aws_iam_role.rockpaperscissors.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "rockpaperscissors" {
  description   = "Play rock paper scissors on Twitter"
  filename      = local.lambda_package
  function_name = local.name
  handler       = "main.lambda_handler"
  role          = aws_iam_role.rockpaperscissors.arn
  timeout       = 15

  source_code_hash = filebase64sha256(local.lambda_package)

  runtime = "python3.8"

  environment {
    variables = {
      API_KEY             = var.api_key
      API_SECRET          = var.api_secret
      ACCESS_TOKEN        = var.access_token
      ACCESS_TOKEN_SECRET = var.access_token_secret
    }
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "every_n_minutes" {
  name                = "every-n-minutes"
  description         = "Fires every n minutes"
  schedule_expression = "rate(10 minutes)"
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
