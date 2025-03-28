[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ornlneutronimaging/HyperCTui/next.svg)](https://results.pre-commit.ci/latest/github/ornlneutronimaging/HyperCTui/next)

# HyperCTui

A user interface to run supervised machine learning-based iterative reconstruction (SVMBIR) code with AI assistance for CT image reconstruction and analysis.

## Quick Start

### Installation

#### Using Pip

```bash
pip install hyperctui
```

#### Using Pixi (Recommended)

```bash
# Install pixi if you don't have it already
curl -fsSL https://pixi.sh/install.sh | bash

# Create a new environment with hyperctui
pixi init --name my-hyperctui-project
cd my-hyperctui-project
pixi add hyperctui

# Start the application
pixi run hyperctui
```

#### Using Conda

```bash
conda install -c neutronimaging hyperctui
```

## Development Guide

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ornlneutronimaging/HyperCTui.git
cd HyperCTui

# Set up development environment with pixi
pixi install

# Start the application
pixi run hyperctui

# Activate the environment
pixi shell
```

### Development Workflow

```bash
# Run tests
pixi run test

# Run linting checks
pixi run ruff check .

# Format code
pixi run ruff format .

# Build the package
pixi run build-pypi

# Build documentation
pixi run build-docs
```

### Adding Dependencies

To add new dependencies:

1. Add Python dependencies to `[project.dependencies]` in `pyproject.toml`, or use `pixi add --pypi <package-name>`.
    - For example, to add `numpy`, run:

      ```bash
      pixi add --pypi numpy
      ```

2. Add pixi/conda dependencies to `[tool.pixi.dependencies]` in `pyproject.toml`, or use `pixi add <package-name>`.
    - For example, to add `scipy`, run:

      ```bash
      pixi add scipy
      ```

3. Run `pixi install` to update your environment.

## How to Use

The application can be started with `hyperctui` in the Python environment it is installed, for development environment managed by `pixi`, use:

```bash
pixi run hyperctui
```

## Known Issues

1. When using `pixi install` for the first time, you might see the following error messages. The solution is to increase your file limit with `ulimit -n 65535` and then run `pixi install` again.

```bash
Too many open files (os error 24) at path
```
