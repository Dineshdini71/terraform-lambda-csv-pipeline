resource "aws_sns_topic" "alerts_notification" {
  name = "lambda-failure-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts_notification.arn
  protocol  = "email"
  endpoint  = var.admin_email
}