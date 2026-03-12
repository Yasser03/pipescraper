# Contributing to pipescraper

Thank you for considering contributing to pipescraper! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/Yasser03/pipescraper.git
   cd pipescraper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**
   ```bash
   pytest tests/ -v
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=pipescraper --cov-report=html

# Run specific test
pytest tests/test_pipescraper.py::TestPipes::test_fetch_links_pipe -v
```

### Writing Tests

- Place tests in `tests/test_pipescraper.py`
- Follow existing test structure and naming conventions
- Use pytest fixtures for common setup
- Mock external dependencies (HTTP requests, etc.)
- Aim for >80% code coverage

Example:
```python
def test_new_feature(sample_article):
    """Test description."""
    result = sample_article >> NewPipeVerb()
    assert isinstance(result, ExpectedType)
```

## 📝 Code Style

### Style Guidelines

- Follow PEP 8
- Use Google-style docstrings
- Maximum line length: 88 characters (Black default)
- Use type hints where appropriate

### Formatting

We use [Black](https://github.com/psf/black) for code formatting:

```bash
# Format all files
black pipescraper/ tests/

# Check formatting without changes
black --check pipescraper/ tests/
```

### Linting

Run flake8 to check for common issues:

```bash
flake8 pipescraper/ tests/
```

## 🎯 Making Changes

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write code
   - Add/update tests
   - Update documentation
   - Follow code style guidelines

3. **Test your changes**
   ```bash
   pytest tests/ -v
   black pipescraper/ tests/
   flake8 pipescraper/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

### Commit Messages

Write clear, descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- Be concise but descriptive
- Reference issues when applicable

Good examples:
- `Add FilterByDate pipe verb for date-based filtering`
- `Fix robots.txt parsing bug in LinkFetcher`
- `Update documentation for ExtractArticles delay parameter`

## 🐛 Reporting Bugs

### Bug Reports

When reporting bugs, please include:

1. **Description** — Clear description of the bug
2. **Reproduction steps** — Minimal code to reproduce
3. **Expected behavior** — What should happen
4. **Actual behavior** — What actually happens
5. **Environment** — Python version, OS, package versions

Example:
```markdown
**Bug Description**
FetchLinks raises TypeError when max_links=None

**Reproduction**
```python
"https://example.com" >> FetchLinks(max_links=None)
```

**Expected**: Should fetch unlimited links
**Actual**: TypeError: 'NoneType' object is not subscriptable

**Environment**: Python 3.10, macOS, pipescraper 0.1.0
```

## 💡 Feature Requests

### Suggesting Features

We welcome feature suggestions! Please:

1. Check existing issues to avoid duplicates
2. Describe the use case clearly
3. Provide examples of desired usage
4. Explain why it would benefit users

## 📚 Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Add docstrings to new classes/functions
- Update examples if behavior changes
- Keep documentation clear and concise

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int = 10) -> bool:
    """
    Short description of function.
    
    Longer description if needed, explaining behavior,
    edge cases, or important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        
    Example:
        >>> result = my_function("test", 20)
        >>> print(result)
        True
    """
    # Implementation
```

## 🔄 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines (Black, flake8)
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Code formatted with Black
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Architecture

### Project Structure

```
pipescraper/
├── __init__.py      # Package exports
├── core.py          # Core classes (Article, Extractors)
├── pipes.py         # Pipe verb classes
└── utils.py         # Utility functions
```

### Adding New Pipe Verbs

1. Create class in `pipes.py` inheriting from `PipeBase`
2. Implement `_execute(self, data)` method
3. Add docstring with examples
4. Export from `__init__.py`
5. Add tests
6. Update README

Example:
```python
class MyNewVerb(PipeBase):
    """
    Description of what this verb does.
    
    Args:
        param1: Description
    
    Example:
        >>> result = data >> MyNewVerb(param1="value")
    """
    
    def __init__(self, param1: str):
        self.param1 = param1
    
    def _execute(self, data):
        """Execute the operation."""
        # Implementation
        return transformed_data
```

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub
- Contact maintainers

---

Thank you for contributing to pipescraper! 🎉

