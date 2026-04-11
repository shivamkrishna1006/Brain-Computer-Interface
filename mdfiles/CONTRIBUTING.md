# Contributing to BCI Interface

We welcome contributions to the Brain-Computer Interface project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Test your code before submitting
- Document your changes

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/bci-eeg-interface.git
cd bci-eeg-interface
git remote add upstream https://github.com/ORIGINAL_OWNER/bci-eeg-interface.git
```

### 2. Setup Development Environment

```bash
# Windows
entrypoint.bat install

# Linux/macOS
chmod +x entrypoint.sh
./entrypoint.sh install

# Or manually
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name

# Good branch names:
# feature/add-attention-mechanism
# bugfix/fix-gpu-memory-leak
# docs/improve-installation-guide
# test/add-model-validation-tests
```

---

## Development Workflow

### Code Style

We follow **PEP 8** with these tools:

```bash
# Format code
black src/ tests/

# Organize imports
isort src/ tests/

# Check code quality
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
make test

# Or directly
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Test specific file
pytest tests/test_training_module.py -v

# Test specific function
pytest tests/test_training_module.py::test_function_name -v
```

### Documentation

Every function/class should have:
```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief description of what the function does.
    
    Longer description explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When value is invalid
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> result = my_function("test", 5)
        >>> print(result)
        'test-5'
    """
    pass
```

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add attention mechanism to CNN-LSTM model"
git commit -m "Fix GPU memory leak in data loader"
git commit -m "Update installation documentation"
git commit -m "Add unit tests for config validation"

# Avoid
git commit -m "fix"
git commit -m "update"
git commit -m "asdf"
```

### Commit Guidelines

- One feature/fix per commit
- Keep commits focused and atomic
- Write meaningful commit messages
- Reference issues: "Fix #123" or "Closes #456"

---

## Types of Contributions

### 1. Bug Fixes

```bash
git checkout -b bugfix/issue-description

# Make changes
# Add test demonstrating the bug
# Fix the bug
# Run: pytest tests/
# Commit and push
```

**Submission**:
1. Describe the bug clearly in the PR
2. Show how to reproduce it
3. Explain your fix
4. Include before/after behavior

### 2. Features

```bash
git checkout -b feature/feature-name

# Implement feature
# Add comprehensive tests
# Update documentation
# Run: make lint test
# Commit and push
```

**Submission**:
1. Describe the feature and its benefits
2. Explain design decisions
3. Show usage examples
4. Ensure backward compatibility

### 3. Documentation

```bash
git checkout -b docs/improvement-name

# Edit documentation files in docs/
# Add/update examples
# Review for clarity and accuracy
# Commit and push
```

**Areas for improvement**:
- Installation/setup guides
- API documentation
- Usage examples
- Troubleshooting guides
- Architecture explanations

### 4. Tests

```bash
git checkout -b test/add-tests-for-feature

# Add tests to tests/
# Ensure at least 80% coverage
# Run: pytest tests/ --cov=src
# Commit and push
```

**Test suggestions**:
- Edge cases
- Error handling
- Integration tests
- Performance tests

### 5. Performance Improvements

```bash
git checkout -b perf/optimize-feature

# Profile the code
# Optimize identified bottlenecks
# Benchmark before/after
# Document improvements
# Commit and push
```

---

## Pull Request Process

### 1. Before Submitting

- [ ] Tests pass: `pytest tests/`
- [ ] Code formatted: `make format`
- [ ] No lint errors: `make lint`
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Commits are clear and atomic

### 2. Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then on GitHub:
1. Create PR against `main` branch
2. Use descriptive title: "Add feature X" or "Fix issue #123"
3. Describe changes clearly
4. Reference related issues
5. Include screenshots/GIFs if relevant

### 3. PR Description Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Changes Made
- Change 1
- Change 2
- Change 3

## Related Issues
Closes #123

## Testing
Describe testing performed:
- [ ] Unit tests added/updated
- [ ] Integration tested
- [ ] Manual testing completed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added code examples
- [ ] Updated README if needed

## Screenshots (if applicable)
Add screenshots for UI changes, new features, etc.

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes
```

### 4. Review Process

- A maintainer will review your PR
- Address any requested changes
- Keep pushing to the same branch (auto-updates PR)
- Once approved, your PR will be merged

---

## Project Areas for Contribution

### High Priority
- [ ] Attention mechanisms for improved accuracy
- [ ] Transfer learning support
- [ ] Hardware driver integration (OpenBCI, Emotiv)
- [ ] Optimization for embedded systems
- [ ] API server implementation

### Medium Priority
- [ ] Ensemble methods
- [ ] Better visualization tools
- [ ] Comprehensive error handling
- [ ] Performance improvements
- [ ] More example notebooks

### Nice to Have
- [ ] Web UI for model training
- [ ] Cloud deployment guides
- [ ] Advanced documentation
- [ ] Community examples
- [ ] Benchmark suite

---

## Development Tips

### Quick Commands

```bash
# Install development dependencies
make dev-install

# Run all checks
make lint test

# Format and check code
make format lint

# Run tests with coverage
make test

# Build Docker image
make docker-build

# Clean up generated files
make clean
```

### Useful Resources

- [Python PEP 8 Style Guide](https://pep8.org/)
- [NumPy Docstring Style](https://numpydoc.readthedocs.io/)
- [TensorFlow Best Practices](https://www.tensorflow.org/guide)
- [Pytest Documentation](https://docs.pytest.org/)

### Development Tools

```bash
# Code formatting
pip install black isort

# Linting
pip install flake8 pylint

# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov

# Pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

---

## Project Structure for Contributors

```
BCI_INTERFACE/
├── src/              # Main source code
├── tests/            # Unit and integration tests
├── scripts/          # Utility scripts
├── examples/         # Example usage
├── docs/             # Documentation
├── config/           # Configuration files
└── main.py          # CLI entry point
```

## Adding New Modules

1. Create module in `src/`
2. Add tests in `tests/test_<module>.py`
3. Document in `docs/`
4. Add example in `examples/` if applicable
5. Update main docs if significant feature

---

## Reporting Issues

### Bug Reports

Create an issue with:

```markdown
## Description
Brief description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## System Information
- OS: [Windows/Linux/macOS]
- Python: [version]
- TensorFlow: [version]

## Error Messages
```
<full error traceback>
```

## Possible Solution
If you have an idea, share it!
```

### Feature Requests

```markdown
## Description
Describe the feature you'd like.

## Motivation
Why would this be useful?

## Proposed Solution
How should it work?

## Alternatives
Other approaches considered?

## Additional Context
Any other information?
```

---

## Getting Help

- **Questions**: Check documentation or open a discussion
- **Bugs**: Create a GitHub issue
- **Features**: Start a discussion before implementing
- **Chat**: Join community channels if available
- **Email**: Contact maintainers directly

---

## Recognition

Contributors are recognized in:
- README.md (Contributors section)
- CHANGELOG.md (Pull request merged)
- GitHub (Automatically via commits)

---

## License

By contributing, you agree your code will be licensed under MIT.

---

## Additional Resources

- [README.md](./README.md) - Project overview
- [docs/](./docs/) - Complete documentation
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Project layout
- [CHANGELOG.md](./CHANGELOG.md) - Version history

---

**Thank you for contributing! 🙏**

Your contributions help make BCI research and development accessible to everyone.

---

## FAQ for Contributors

**Q: How long until my PR is reviewed?**
A: Typically within 1-7 days depending on complexity.

**Q: Can I work on multiple features?**
A: Yes, but one PR per feature is recommended.

**Q: Do I need to sign anything?**
A: No, just submit your PR. Contributing implies agreement with MIT license.

**Q: Can my feature be rejected?**
A: Yes, if it doesn't align with project goals. Discuss first in an issue!

**Q: How do I update my fork?**
A: 
```bash
git fetch upstream
git rebase upstream/main
git push origin main
```

---

Version: 1.0.0  
Last Updated: 2024
