# Contributing to Blocket (unofficial)

Thank you for considering contributing to this project! This is a community-driven unofficial integration.

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `python3 tests/test_parsing_standalone.py`
5. Commit your changes: `git commit -m "feat: add your feature"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a Pull Request

## Development Setup

### Local Development

```bash
git clone https://github.com/Vortitron/ha-blocket.git
cd ha-blocket

# Run standalone tests
python3 tests/test_parsing_standalone.py

# Test against live Blocket (requires aiohttp)
pip3 install aiohttp
python3 tests/test_live_blocket.py
```

### Testing in Home Assistant

1. Copy `custom_components/blocket/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.blocket: debug
```

4. Add integration via UI and test

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Code Style

- Follow [PEP 8](https://pep8.org/)
- Use tabs for indentation (per project style)
- Type hints for all function signatures
- Docstrings for all public functions/classes
- British English in comments and documentation

## Commit Convention

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Examples:

```
feat: add support for recommerce URL format
fix: handle missing price in JSON-LD parsing
docs: update README with automation examples
test: add edge case for free listings
```

## Code Guidelines

### DO

- ✅ Reuse functions wherever possible
- ✅ Use tabs, not spaces
- ✅ Pass data through function parameters (no `export let` or exported objects/arrays)
- ✅ Use ES Modules and modern Python
- ✅ Verify information before implementation
- ✅ Include proper error handling and logging
- ✅ Write unit tests for new code
- ✅ Handle edge cases
- ✅ Add assertions to validate assumptions

### DON'T

- ❌ Create mock functions for actual logic (mocks only for testing)
- ❌ Create placeholder code unless explicitly needed (and warn about it)
- ❌ Make files > 1500 lines (refactor instead)
- ❌ Use dynamic imports
- ❌ Hard-code values (use named constants)
- ❌ Assume or speculate without evidence

## What to Contribute

### High Priority

- Bug fixes (especially if Blocket changes their page structure)
- Better error handling
- Additional unit tests
- Documentation improvements
- Translation updates (Swedish improvements welcome!)

### Medium Priority

- Support for additional Blocket URL formats
- Better parsing of location data
- Improved logging
- Performance optimizations

### Nice to Have

- More sensor types
- Service calls (e.g. manual refresh)
- Config validation improvements
- Additional translations (Danish, Norwegian)

## Blocket Page Structure Changes

If Blocket changes their page structure and the integration breaks:

1. Fetch a current search page: `curl -A "HomeAssistant-Blocket-unofficial" https://www.blocket.se/mobility/search/car > sample.html`
2. Look for JSON-LD structured data (search for `seoStructuredData`)
3. Update `coordinator.py` parsing logic to match new structure
4. Add/update test fixtures
5. Test with `python3 tests/test_live_blocket.py`
6. Open a PR with clear explanation of what changed

## Questions?

Open an issue or start a discussion on GitHub.

## Legal / Ethics

- This is an **unofficial** integration, not affiliated with Blocket AB or Schibsted
- The integration should only perform the same HTTP requests a normal browser would
- Be respectful of Blocket's servers (no aggressive polling)
- No scraping of user data or private information
- Comply with Blocket's Terms of Service

---

**Thank you for contributing!** 🎉
