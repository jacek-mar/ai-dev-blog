# Contributing to AI Developers Blog

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear title describing the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- Clear description of the enhancement
- Use case or problem it solves
- Proposed implementation (if applicable)

### Adding Blog Sources

To add a new blog source:

1. Verify the blog has RSS feed or scrapable HTML
2. Add source to `sources.json`:
   ```json
   {
     "name": "Blog Name",
     "url": "https://example.com",
     "rss": "https://example.com/feed.xml",
     "max_articles": 20
   }
   ```
3. Test locally
4. Submit pull request

### Code Contributions

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/YourFeature`)
3. **Make** your changes
4. **Test** locally
5. **Commit** with clear message
6. **Push** to your fork
7. **Create** pull request

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Testing

Before submitting:
- Test scraper: `python scraper/scraper.py`
- Test generator: `python generator/site_generator.py`
- Verify site renders correctly
- Check logs for errors

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new blog source`
- `fix: Resolve RSS parsing error`
- `docs: Update README with deployment steps`
- `refactor: Simplify article deduplication logic`

## 🔍 Code Review Process

All contributions go through code review:
1. Automated checks (if implemented)
2. Manual review by maintainers
3. Feedback and requested changes
4. Approval and merge

## 📝 Documentation

When adding features:
- Update README.md if user-facing
- Add inline code comments
- Update configuration examples
- Document new dependencies

## 🤖 AI Enhancement

If modifying AI integration:
- Maintain backward compatibility
- Test with KiloCode webhooks
- Verify fallback behavior
- Document prompt changes

## 🌐 Site Generation

If modifying site generator:
- Test with various article counts
- Verify responsive design
- Check RSS feed validity
- Ensure accessibility

## ❓ Questions?

Feel free to open an issue for:
- Clarification on contribution process
- Technical questions
- Feature discussions
- General feedback

## 🙏 Thank You!

Your contributions help make this project better for everyone!
