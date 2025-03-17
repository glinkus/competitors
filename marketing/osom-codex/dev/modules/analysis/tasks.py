import shlex
import subprocess
import os
from celery import shared_task

@shared_task
def run_spider(website_id, website_name):
    env = os.environ.copy()
    env['SCRAPY_SETTINGS_MODULE'] = 'competitors_scraper.settings'
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.join(BASE_DIR, 'competitors_scraper')
    env['PYTHONPATH'] = BASE_DIR + os.pathsep + env.get('PYTHONPATH', '')
    
    cmd = f"scrapy crawl full_site_spider -a website_id={website_id} -a website_name='{website_name}'"
    args = shlex.split(cmd)
    
    # Redirect output to a file
    output_file = os.path.join(project_root, 'spider_output.txt')
    with open(output_file, "w") as f:
        result = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=project_root)
    
    if result.returncode != 0:
        raise Exception(f"Spider process failed, see log at {output_file}")
    
    return f"Spider output logged to {output_file}"
