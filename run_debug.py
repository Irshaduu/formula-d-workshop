import os
import django
import sys
import io
import traceback
from django.conf import settings

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings

def run_failing_test():
    # Redirect stdout and stderr to a buffer
    out = io.StringIO()
    sys.stdout = out
    sys.stderr = out
    
    try:
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False, failfast=False)
        # Run ALL tests
        test_runner.run_tests(['workshop', 'inventory'])
    except Exception:
        traceback.print_exc()
    
    # Write the buffer to a file
    with open('full_test_log.txt', 'w', encoding='utf-8') as f:
        f.write(out.getvalue())

if __name__ == "__main__":
    run_failing_test()
