"""Pytest configuration and fixtures."""
import os
import pytest
import tempfile


@pytest.fixture(scope='function')
def test_app():
    """Create and configure a test application instance."""
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)

    # Import here to avoid issues with module-level configuration
    from main import app, db

    # Create a temporary database path (not file descriptor)
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f'test_components_{os.getpid()}.db')

    # Store original config
    original_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')

    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Push an application context
    ctx = app.app_context()
    ctx.push()

    # Create database tables
    db.create_all()

    yield app

    # Cleanup
    db.session.remove()
    db.drop_all()
    ctx.pop()

    # Restore original config
    app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri

    # Remove the temporary database file
    try:
        if os.path.exists(db_path):
            os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(test_app):
    """Create a test client for the application."""
    return test_app.test_client()


@pytest.fixture
def sample_component():
    """Return sample component data for testing."""
    return {
        'name': 'Arduino Uno',
        'type': 'Microcontroller',
        'version': 'R3',
        'description': 'ATmega328P based microcontroller board',
        'amount': 5,
        'datasheet_url': 'https://example.com/arduino-uno.pdf'
    }
