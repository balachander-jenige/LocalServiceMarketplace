###########################################
# SECURITY GROUPS
###########################################
# ALB Security Group – allows HTTP/HTTPS from internet
resource "aws_security_group" "alb_sg" {
  name        = "${var.project}-alb-sg"
  description = "Allow inbound HTTP/HTTPS to ALB"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # (Optional) If you plan to support HTTPS later
  # ingress {
  #   description = "Allow HTTPS from anywhere"
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-alb-sg"
  }
}

# Target group security group (for backend EC2s or EKS nodes)
resource "aws_security_group" "target_sg" {
  name        = "${var.project}-target-sg"
  description = "Allow inbound from ALB to backend services"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-target-sg"
  }
}

###########################################
# LOAD BALANCER SETUP
###########################################
resource "aws_lb" "app_alb" {
  name               = "${var.project}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.public_subnets

  tags = {
    Name = "${var.project}-alb"
  }
}

###########################################
# TARGET GROUP
###########################################
resource "aws_lb_target_group" "app_tg" {
  name        = "${var.project}-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = var.target_type # "instance" or "ip"

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200-399"
  }

  tags = {
    Name = "${var.project}-tg"
  }
}

###########################################
# ALB LISTENER
###########################################
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}
