from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///components.db'
db = SQLAlchemy(app)

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50))
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, nullable=False)
    datasheet_url = db.Column(db.String(200))

    def __repr__(self):
        return f'<Component {self.name} ({self.type})>'

@app.route('/components', methods=['GET'])
def get_components():
    components = Component.query.all()
    return jsonify([component_to_dict(c) for c in components])

@app.route('/components', methods=['POST'])
def create_component():
    data = request.get_json()
    component = Component(
        name=data['name'],
        type=data['type'],
        version=data.get('version'),
        description=data['description'],
        amount=data['amount'],
        datasheet_url=data['datasheet_url']
    )
    db.session.add(component)
    db.session.commit()
    return jsonify(component_to_dict(component)), 201

@app.route('/components/<int:component_id>', methods=['GET'])
def get_component(component_id):
    component = Component.query.get_or_404(component_id)
    return jsonify(component_to_dict(component))

@app.route('/components/<int:component_id>', methods=['PUT'])
def update_component(component_id):
    component = Component.query.get_or_404(component_id)
    data = request.get_json()
    component.name = data['name']
    component.type = data['type']
    component.version = data.get('version')
    component.description = data['description']
    component.amount = data['amount']
    component.datasheet_url = data['datasheet_url']
    db.session.commit()
    return jsonify(component_to_dict(component))

@app.route('/components/<int:component_id>', methods=['DELETE'])
def delete_component(component_id):
    component = Component.query.get_or_404(component_id)
    db.session.delete(component)
    db.session.commit()
    return '', 204

def component_to_dict(component):
    return {
        'id': component.id,
        'name': component.name,
        'type': component.type,
        'version': component.version,
        'description': component.description,
        'amount': component.amount,
        'datasheet_url': component.datasheet_url
    }

if __name__ == '__main__':
    app.run(debug=True)