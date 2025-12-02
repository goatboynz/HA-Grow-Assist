# Contributing to Grow Room Manager

Thank you for your interest in contributing!

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Use the bug report template
3. Include Home Assistant and integration versions
4. Provide relevant logs

### Feature Requests

1. Check existing feature requests
2. Use the feature request template
3. Describe the use case clearly

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Home Assistant
5. Submit a pull request

## Development Setup

1. Clone the repository
2. Copy `custom_components/grow_room_manager` to your HA config
3. Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.grow_room_manager: debug
```

## Code Style

- Follow Home Assistant development guidelines
- Use type hints
- Add docstrings to functions
- Keep code readable and maintainable

## Questions?

Open a discussion or issue on GitHub.
