variable "group_name" {
  description = "Name of your workshops group"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$", var.group_name))
    error_message = "The group_name value must be a valid slug. It can only contain lowercase letters, numbers, and hyphens, and cannot begin or end with a hyphen."
  }
}

variable "vpc_id" {
  description = "ID of the VPC to use. Provided by Deployed."
  type = string
  default = "vpc-08093a050fe04a70e"
}

variable "vpc_subnet_id" {
  description = "ID of the subnet inside the VPC to create VMs. Provided by Deployed."
  type = string
  default = "subnet-025d966de6659dfcd"
}

variable "vm_ingress_rules" {
    description = "List of objects defining which ports are exposed on the created VM"
    type = list(object({
        cidr = string
        port = number
        protocol = string
    }))
}

variable "vm_public_key" {
    description = "Public key to be deployed to the created vm"
    type = string 
}