"""Ponto de entrada da aplicação (servidor local e PythonAnywhere)."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
