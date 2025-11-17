#!/bin/bash
# Test runner script for local development and CI

set -e

echo "🧪 Running Markboard Test Suite..."
echo "=================================="

# Set test environment variables
export FLASK_ENV=testing
export JWT_SECRET=test_jwt_secret
export MYSQL_HOST=${MYSQL_HOST:-localhost}
export MYSQL_PORT=${MYSQL_PORT:-3306}
export MYSQL_USER=${MYSQL_USER:-test_user}
export MYSQL_PASSWORD=${MYSQL_PASSWORD:-test_password}
export MYSQL_DATABASE=${MYSQL_DATABASE:-test_markboard}

# Install dependencies if needed
echo "📦 Installing dependencies..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests with coverage
echo "🔍 Running tests with coverage..."
python -m pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    --cov-fail-under=70 \
    -v

echo ""
echo "✅ Test run complete!"
echo "📊 Coverage report available at: htmlcov/index.html"
echo "📋 XML report available at: coverage.xml"

# Check if coverage threshold was met
if [ $? -eq 0 ]; then
    echo "🎉 All tests passed and coverage threshold met!"
else
    echo "❌ Tests failed or coverage below threshold (70%)"
    exit 1
fi