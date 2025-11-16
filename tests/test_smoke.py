"""Basic smoke tests for Component Inventory application."""
import json
import pytest


class TestApplicationStartup:
    """Test application startup and basic configuration."""

    def test_app_exists(self, test_app):
        """Test that the application instance exists."""
        assert test_app is not None

    def test_app_is_testing(self, test_app):
        """Test that the application is in testing mode."""
        assert test_app.config['TESTING'] is True

    def test_client_exists(self, client):
        """Test that the test client is available."""
        assert client is not None


class TestComponentsEndpoints:
    """Test basic CRUD operations on components endpoints."""

    def test_get_empty_components_list(self, client):
        """Test GET /components returns empty list initially."""
        response = client.get('/components')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_component(self, client, sample_component):
        """Test POST /components creates a new component."""
        response = client.post(
            '/components',
            data=json.dumps(sample_component),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == sample_component['name']
        assert data['type'] == sample_component['type']
        assert data['version'] == sample_component['version']
        assert data['amount'] == sample_component['amount']
        assert 'id' in data

    def test_get_component_by_id(self, client, sample_component):
        """Test GET /components/<id> returns the correct component."""
        # First create a component
        create_response = client.post(
            '/components',
            data=json.dumps(sample_component),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        component_id = created_data['id']

        # Then retrieve it
        response = client.get(f'/components/{component_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == component_id
        assert data['name'] == sample_component['name']

    def test_get_nonexistent_component(self, client):
        """Test GET /components/<id> with nonexistent ID returns 404."""
        response = client.get('/components/999')
        assert response.status_code == 404

    def test_update_component(self, client, sample_component):
        """Test PUT /components/<id> updates a component."""
        # First create a component
        create_response = client.post(
            '/components',
            data=json.dumps(sample_component),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        component_id = created_data['id']

        # Update the component
        updated_data = sample_component.copy()
        updated_data['amount'] = 10
        updated_data['description'] = 'Updated description'

        response = client.put(
            f'/components/{component_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['amount'] == 10
        assert data['description'] == 'Updated description'

    def test_delete_component(self, client, sample_component):
        """Test DELETE /components/<id> removes a component."""
        # First create a component
        create_response = client.post(
            '/components',
            data=json.dumps(sample_component),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        component_id = created_data['id']

        # Delete the component
        response = client.delete(f'/components/{component_id}')
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f'/components/{component_id}')
        assert get_response.status_code == 404

    def test_list_multiple_components(self, client, sample_component):
        """Test GET /components returns multiple components."""
        # Create first component
        client.post(
            '/components',
            data=json.dumps(sample_component),
            content_type='application/json'
        )

        # Create second component
        second_component = sample_component.copy()
        second_component['name'] = 'Raspberry Pi 4'
        second_component['type'] = 'Single Board Computer'
        client.post(
            '/components',
            data=json.dumps(second_component),
            content_type='application/json'
        )

        # List all components
        response = client.get('/components')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2


class TestComponentValidation:
    """Test component data validation."""

    def test_create_component_without_required_fields(self, client):
        """Test POST /components fails without required fields."""
        incomplete_component = {
            'name': 'Test Component'
            # Missing required fields: type, amount, description, datasheet_url
        }

        response = client.post(
            '/components',
            data=json.dumps(incomplete_component),
            content_type='application/json'
        )
        # Expect either 400 Bad Request or 500 Internal Server Error
        assert response.status_code >= 400

    def test_create_component_with_optional_version(self, client):
        """Test POST /components works with optional version field."""
        component = {
            'name': 'Generic LED',
            'type': 'LED',
            'description': 'Red LED 5mm',
            'amount': 100,
            'datasheet_url': 'https://example.com/led.pdf'
            # version is optional
        }

        response = client.post(
            '/components',
            data=json.dumps(component),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['version'] is None or data['version'] == ''
