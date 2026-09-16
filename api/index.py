import os
import sys

# Ensure the root directory is on the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deep_air_learning_prediction.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
