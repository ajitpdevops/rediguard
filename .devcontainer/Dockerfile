# ------------------------------------
# CLOUDAI PROJECT DEVCONTAINER
# ------------------------------------
# This Dockerfile builds a development container for cloud development
# with tools for AWS, Docker, Terraform and other cloud infrastructure work

# Base image: Ubuntu 22.04 LTS (Jammy Jellyfish)
FROM ubuntu:22.04

# Container metadata
LABEL org.opencontainers.image.authors="CloudAI Platform Team"
LABEL org.opencontainers.image.source="https://github.com/ajitpdevops/redis8-poc"

# Environment setup
# - Prevents interactive prompts during package installation
# - Sets default locale to US English with UTF-8 encoding
# - Sets default shell to bash
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV SHELL=/bin/bash

# Install base system dependencies
# - Core development tools: git, build-essential, etc.
# - Shell utilities: bash, zsh, completions
# - Text editors: vim, nano
# - Network tools: curl, wget, iputils-ping, net-tools
# - Document processing: asciidoctor, jq
# - System utilities: htop, sudo, etc.
# - WSL integration: wslu (for Windows Subsystem for Linux utilities)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    asciidoctor \
    bash \
    bash-completion \
    build-essential \
    ca-certificates \
    curl \
    git \
    git-lfs \
    gosu \
    gnupg \
    htop \
    iputils-ping \
    jq \
    less \
    locales \
    lsb-release \
    man-db \
    net-tools \
    nano \
    software-properties-common \
    sudo \
    unzip \
    vim \
    wget \
    wslu \
    zsh && \
    locale-gen en_US.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/*

# Create non-root user for development
# - Creates 'cloudai' user with UID/GID 1000 (standard for first user)
# - Adds user to sudoers with passwordless sudo access
# - Sets default shell to bash
ARG USERNAME=cloudai
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 0440 /etc/sudoers.d/${USERNAME} && \
    chsh -s /bin/bash ${USERNAME}

# Set up VS Code Server path as a volume
# - This preserves VS Code extensions between container rebuilds
# - Creates and configures directory ownership for the non-root user
ARG VSC_SERVER_PATH="/home/${USERNAME}/.vscode-server"
RUN mkdir -p "${VSC_SERVER_PATH}" \
    && chown ${USERNAME}:${USERNAME} "${VSC_SERVER_PATH}"
VOLUME [ "${VSC_SERVER_PATH}" ]

# Install Python 3.10 and pip
# - Used for Python development and for tools that depend on Python
# - Configurable version via build arg
ARG PYTHON_VERSION=3.10
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/*

# Install Act CLI
# - Tool for running GitHub Actions locally
# - Useful for testing workflows without pushing to GitHub
RUN curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Install AWS CLI v2 - with architecture detection
# - Supports both amd64 (x86_64) and arm64 (aarch64) architectures
# - Configurable version via build arg
# - Used for interacting with AWS services
ARG AWS_CLI_VERSION=2.15.0
RUN PLATFORM=$(dpkg --print-architecture) && \
    case "$PLATFORM" in \
    amd64) ARCH="x86_64" ;; \
    arm64) ARCH="aarch64" ;; \
    *) echo "Unsupported architecture: $PLATFORM" && exit 1 ;; \
    esac && \
    curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}-${AWS_CLI_VERSION}.zip" -o /tmp/awscliv2.zip && \
    unzip -q /tmp/awscliv2.zip -d /tmp && \
    /tmp/aws/install && \
    rm -rf /tmp/aws /tmp/awscliv2.zip && \
    aws --version

# Install AWS SSO Utility
# - Helper tool for working with AWS SSO (Single Sign-On)
# - Makes managing AWS SSO credentials easier
# - Configurable version via build arg
ARG AWS_SSO_UTIL_VERSION=4.33.0
RUN pip3 install aws-sso-util==${AWS_SSO_UTIL_VERSION} \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* \
    && aws-sso-util --version

# Install Docker with Docker Compose
# - Enables container management from inside the dev container
# - Includes Docker CE, Docker CLI, Docker Buildx, and Docker Compose
# - Configurable version via build arg
# - Adds current user to docker group for non-root Docker access
ARG DOCKER_VERSION=5:25.0.2-1
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update -qq && \
    apt-get install -y "docker-ce=${DOCKER_VERSION}~ubuntu.22.04~jammy" "docker-ce-cli=${DOCKER_VERSION}~ubuntu.22.04~jammy" docker-buildx-plugin docker-compose-plugin && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* && \
    docker --version
RUN usermod -aG docker ${USERNAME}

# Install git pre-commit hooks framework
# - Framework for managing git pre-commit hooks
# - Helps maintain code quality through automatic checks
# - Supports many linters and formatters
RUN pip3 install pre-commit && rm -rf /root/.cache

# Install GitHub CLI (gh)
# - Command-line tool for interacting with GitHub
# - Supports PRs, issues, repos, and other GitHub features from terminal
# - Configurable version via build arg
ARG GH_CLI_VERSION=2.4.0
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* && \
    gh --version

# Install terraform-docs
# - Utility for generating documentation from Terraform modules
# - Auto-generates markdown documentation for Terraform modules
# - Configurable version via build arg
ARG TERRAFORM_DOCS_VERSION=v0.17.0
RUN curl -sSLo terraform-docs.tar.gz https://github.com/terraform-docs/terraform-docs/releases/download/${TERRAFORM_DOCS_VERSION}/terraform-docs-${TERRAFORM_DOCS_VERSION}-linux-$(dpkg --print-architecture).tar.gz && \
    tar -xzf terraform-docs.tar.gz terraform-docs && \
    mv terraform-docs /usr/local/bin/ && chmod +x /usr/local/bin/terraform-docs && \
    rm terraform-docs.tar.gz

# Install TFLint - Terraform linter
# - Static analysis tool for Terraform code
# - Catches errors and enforces best practices
# - Architecture-specific binary installation
# - Configurable version via build arg
ARG TFLINT_VERSION=v0.50.3
RUN curl -sSL "https://github.com/terraform-linters/tflint/releases/download/${TFLINT_VERSION}/tflint_linux_$(dpkg --print-architecture).zip" -o /tmp/tflint.zip && \
    unzip /tmp/tflint.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/tflint && \
    rm -f /tmp/tflint.zip && \
    tflint --version

# Install TFSEC - Terraform security scanner
# - Static analysis security scanner for Terraform code
# - Checks for potential security issues and vulnerabilities
# - Architecture-specific binary installation
# - Configurable version via build arg
ARG TFSEC_VERSION=v1.28.1
RUN curl -sSL "https://github.com/aquasecurity/tfsec/releases/download/${TFSEC_VERSION}/tfsec-linux-$(dpkg --print-architecture)" -o /usr/local/bin/tfsec && \
    chmod +x /usr/local/bin/tfsec && \
    tfsec --version

# Install Terraform - Infrastructure as Code tool
# - Core tool for provisioning and managing cloud infrastructure
# - Architecture-specific binary installation (supports both amd64 and arm64)
# - Configurable version via build arg
ARG TERRAFORM_VERSION=1.11.1
RUN PLATFORM=$(dpkg --print-architecture) \
    && wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${PLATFORM}.zip \
    && unzip terraform_*.zip \
    && mv terraform /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm terraform_*.zip \
    && terraform version

# Install Oh My Zsh - ZSH configuration framework
# - Enhances ZSH shell with plugins, themes, and configuration
# - Installed system-wide in /etc for all users
# - Configurable version via build arg
ARG OH_MY_ZSH_VERSION=master
RUN mkdir -p /etc/oh-my-zsh && \
    curl -fsSL https://github.com/ohmyzsh/ohmyzsh/archive/refs/heads/${OH_MY_ZSH_VERSION}.tar.gz | \
    tar -xz --strip-components=1 -C /etc/oh-my-zsh && \
    find /etc/oh-my-zsh -type d -exec chmod g-w,o-w {} \;

# Install Oh My Bash - Bash configuration framework
# - Enhances Bash shell with plugins, themes, and configuration
# - Similar to Oh My Zsh but for Bash
# - Installed system-wide in /etc for all users
# - Configurable version via build arg
ARG OH_MY_BASH_VERSION=master
RUN mkdir -p /etc/oh-my-bash && \
    curl -fsSL https://github.com/ohmybash/oh-my-bash/archive/refs/heads/${OH_MY_BASH_VERSION}.tar.gz | \
    tar -xz --strip-components=1 -C /etc/oh-my-bash

# Copy custom devcontainer scripts and configurations
# - Copies files from the .devcontainer/etc directory to /etc in the container
# - These include shell configurations, utilities, and helper functions
COPY ./etc/ /etc/

# Make all shell scripts in the devcontainer directory executable
# - Ensures all custom scripts have proper execution permissions
RUN find /etc/devcontainer/ -type f -name "*.sh" -exec chmod +x {} \;

# Configure bash to source custom devcontainer configuration for all interactive shells
# - This loads custom aliases, functions, and environment variables
# - /etc/devcontainer/shell/.bashrc is sourced from /etc/bash.bashrc to apply to all interactive shells
RUN printf '\n# DevContainer custom script\nsource /etc/devcontainer/shell/.bashrc\n' \
    >> /etc/bash.bashrc

# Switch from root to the non-root user for better security and permissions
# - All subsequent commands will run as the non-root user
# - The USERNAME variable was set earlier (default: cloudai)
USER ${USERNAME}