import sys

print("🔧 Loading Flask context...")

sys.path.insert(0, '/app')

try:
    from main import create_app
    from app.extensions import db  # noqa

    # Create and push Flask context
    app = create_app()
    app_context = app.app_context()
    app_context.push()

    # Import all models dynamically
    import app.models

    # Get all model classes from the models module
    model_classes = {}
    for attr_name in dir(app.models):
        attr = getattr(app.models, attr_name)
        # Check if it's a class and likely a SQLAlchemy model
        if (
            isinstance(attr, type)
            and hasattr(attr, '__tablename__')
            and hasattr(attr, 'query')
        ):
            model_classes[attr_name] = attr
            # Make it available globally
            globals()[attr_name] = attr

except Exception as e:
    print(f"❌ Flask setup failed: {e}")
    print("Make sure the Flask app is properly configured")
    import traceback

    traceback.print_exc()
