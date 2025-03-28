[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ornlneutronimaging/HyperCTui/next.svg)](https://results.pre-commit.ci/latest/github/ornlneutronimaging/HyperCTui/next)
[![codecov](https://codecov.io/gh/ornlneutronimaging/HyperCTui/graph/badge.svg?token=OcQABZITUc)]

# HyperCTui

A user interface to run supervised machine learning-based iterative reconstruction (SVMBIR) code with AI assistance for CT image reconstruction and analysis.

## Quick Start

### Installation

#### Using Pip

```bash
pip install hyperctui
```

The package requires `tomopy` to function, which can be installed either with `conda` or directly from source [Github](https://github.com/tomopy/tomopy).
Make sure you install `tomopy` before running the application if installed with `pip`.

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

## Contribution Guidelines

### For Neutron Data Project Developers at ORNL

- Contact the project maintainer for developer access to the repository
- Always create feature branches based off the `next` branch
- All tests must pass before merging your changes
- Submit a pull request for review, linking any related issues

### For External Developers

- Please fork the repository and make your suggested edits there
- Submit a pull request from your fork to our `next` branch
- Ensure all tests pass before submitting your PR

### Coding Style

- Run `pixi run pre-commit install` at least once in your checkout repository to ensure pre-commit hooks are installed locally
- These hooks will automatically check and fix many common style issues
- We follow PEP 8 guidelines with certain exceptions defined in our configuration files

### Type Hinting and Documentation

- We prefer using type hinting for all function parameters and return values:

  ```python
  def process_image(image_data: np.ndarray, factor: float = 1.0) -> np.ndarray:
      """Process the given image data.

      Parameters
      ----------
      image_data : np.ndarray
          The input image as a numpy array
      factor : float, optional
          Scaling factor to apply, by default 1.0

      Returns
      -------
      np.ndarray
          The processed image
      """
  ```

- Use NumPy style docstrings for all public methods and functions

### Testing

- New features should have corresponding unit tests
- We do not force Test-Driven Development (TDD), but we highly recommend it
- Aim for high test coverage, especially for critical functionality
- Tests are automatically run on PR submission

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
