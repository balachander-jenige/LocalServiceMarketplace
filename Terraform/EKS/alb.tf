# =============================================================================
# APPLICATION LOAD BALANCER (ALB)
# =============================================================================
# Creates ALB in public subnets to route traffic to EKS cluster in private subnets

# -----------------------------------------------------------------------------
# APPLICATION LOAD BALANCER
# -----------------------------------------------------------------------------
resource "aws_lb" "main" {
  name               = "${var.cluster_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.public_subnet_ids

  enable_deletion_protection = var.enable_deletion_protection

  tags = {
    Name        = "${var.cluster_name}-alb"
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# ALB TARGET GROUP (for EKS services)
# -----------------------------------------------------------------------------
resource "aws_lb_target_group" "eks_services" {
  name     = "freelancer-eks-tg"  # Shortened to fit 32 char limit
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.cluster_name}-eks-tg"
  }
}

# -----------------------------------------------------------------------------
# ALB LISTENERS
# -----------------------------------------------------------------------------

# HTTP Listener (redirects to HTTPS if certificate is available)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = var.create_certificate ? "redirect" : "forward"
    
    dynamic "redirect" {
      for_each = var.create_certificate ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
    
    dynamic "forward" {
      for_each = var.create_certificate ? [] : [1]
      content {
        target_group {
          arn = aws_lb_target_group.eks_services.arn
        }
      }
    }
  }
}

# HTTPS Listener (only if certificate is created)
resource "aws_lb_listener" "https" {
  count             = var.create_certificate ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate_validation.main[0].certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.eks_services.arn
  }
}

# -----------------------------------------------------------------------------
# SSL CERTIFICATE (Optional)
# -----------------------------------------------------------------------------
resource "aws_acm_certificate" "main" {
  count             = var.create_certificate ? 1 : 0
  domain_name       = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.cluster_name}-cert"
  }
}

resource "aws_acm_certificate_validation" "main" {
  count           = var.create_certificate ? 1 : 0
  certificate_arn = aws_acm_certificate.main[0].arn
  
  timeouts {
    create = "5m"
  }
}