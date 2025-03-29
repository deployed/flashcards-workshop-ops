# OpenTofu Cheatsheet

OpenTofu is an open-source infrastructure as code tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share.

## Core Concepts

- **Provider**: Plugin that OpenTofu uses to interact with cloud providers, SaaS providers, and other APIs
- **Resource**: A component of your infrastructure (e.g., virtual machine, database)
- **Module**: Reusable container for multiple resources that are used together
- **State**: OpenTofu's record of all managed resources and their properties
- **Variables**: Parameters for configuring your infrastructure
- **Outputs**: Return values from your infrastructure

## Basic Commands

| Command | Description |
|---------|-------------|
| `tofu init` | Initialize a working directory containing configuration files |
| `tofu plan` | Create an execution plan to preview changes |
| `tofu apply` | Apply the changes required to reach the desired state |
| `tofu destroy` | Destroy all resources managed by the current configuration |
| `tofu validate` | Validate configuration files |
| `tofu fmt` | Reformat configuration files to canonical style |
| `tofu show` | Show the current state or a saved plan |
| `tofu state list` | List resources in the state file |
| `tofu output` | Show output values from the state file |

## Configuration Basics

### Provider Configuration
```hcl
provider "aws" {
  region = "us-east-1"
}
```

### Resource Definition
```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "example-instance"
  }
}
```

### Variables
```hcl
# In variables.tf
variable "instance_type" {
  description = "The type of EC2 instance to launch"
  type        = string
  default     = "t2.micro"
}

# Usage in main.tf
resource "aws_instance" "example" {
  instance_type = var.instance_type
  # ...
}
```

### Outputs
```hcl
output "instance_ip" {
  description = "The public IP of the instance"
  value       = aws_instance.example.public_ip
}
```

## Common Workflows

### Initialize and Apply Changes
```bash
# Initialize the directory
tofu init

# Create and review a plan
tofu plan

# Apply changes
tofu apply
```

### Working with State
```bash
# List resources in state
tofu state list

# Show details of a specific resource
tofu state show aws_instance.example

# Remove a resource from state (without destroying it)
tofu state rm aws_instance.example
```