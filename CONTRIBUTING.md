# Contributing to MoltPal

Thanks for your interest in contributing! This is an early-stage project and we welcome all kinds of contributions.

## Ways to Contribute

- 🐛 **Bug Reports** - Found a bug? Open an issue with reproduction steps
- 💡 **Feature Requests** - Have an idea? Let's discuss it
- 📝 **Documentation** - Improve docs, add examples, fix typos
- 🔧 **Code** - Submit pull requests for bugs or features
- 🧪 **Testing** - Help test edge cases and write tests

## Development Setup

1. **Fork and clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/moltpal.git
cd moltpal
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up database**
```bash
# Create PostgreSQL database
createdb moltpal_dev

# Copy env file
cp .env.example .env

# Edit .env with your database URL
# Run migrations
npm run db:migrate
```

4. **Start development server**
```bash
npm run dev
```

## Code Style

- Use ES6+ features
- 2 spaces for indentation
- Clear, descriptive variable names
- Add comments for complex logic
- Keep functions small and focused

## Pull Request Process

1. **Create a feature branch**
```bash
git checkout -b feature/my-feature
```

2. **Make your changes**
- Write clear commit messages
- Test your changes locally
- Update documentation if needed

3. **Submit PR**
- Describe what you changed and why
- Reference any related issues
- Request review from maintainers

## Testing

We don't have a full test suite yet, but please:
- Test your changes manually
- Verify API endpoints work as expected
- Check for edge cases
- Don't break existing functionality

## Questions?

Open an issue or reach out to [@alallos](https://github.com/alallos)

## Code of Conduct

Be respectful. Be constructive. Help make this project awesome for everyone.
