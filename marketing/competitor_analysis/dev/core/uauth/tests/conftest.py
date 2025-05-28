import pytest
import os
from django.conf import settings

@pytest.fixture(scope='session')
def create_test_templates():
    template_dir = os.path.join(settings.BASE_DIR, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    base_template_path = os.path.join(template_dir, 'base_test.html')
    if not os.path.exists(base_template_path):
        with open(base_template_path, 'w') as f:
            f.write('<!DOCTYPE html><html><body>{% block content %}{% endblock %}</body></html>')
    
    parea_dir = os.path.join(template_dir, 'parea')
    os.makedirs(parea_dir, exist_ok=True)
    parea_layout_path = os.path.join(parea_dir, 'layout_test.html')
    if not os.path.exists(parea_layout_path):
        with open(parea_layout_path, 'w') as f:
            f.write('<!DOCTYPE html><html><body>{% block content %}{% endblock %}</body></html>')
    
    yield
