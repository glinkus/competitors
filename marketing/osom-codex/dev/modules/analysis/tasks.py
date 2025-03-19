import shlex
import subprocess
import os
from time import sleep
from celery import shared_task
from modules.analysis.models import Page

@shared_task
def run_one_page_spider(website_id, website_name):
    # Set up environment and project paths
    env = os.environ.copy()
    env['SCRAPY_SETTINGS_MODULE'] = 'competitors_scraper.settings'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.join(BASE_DIR, 'competitors_scraper')
    env['PYTHONPATH'] = BASE_DIR + os.pathsep + env.get('PYTHONPATH', '')
    output_file = os.path.join(project_root, f'spider_output_{website_id}.txt')

    while True:
        # Query for pages for this website that haven't been visited
        unvisited_pages = list(
            Page.objects.filter(website_id=website_id, visited=False)
            .values_list("url", flat=True)
        )
        if not unvisited_pages:
            return "No unvisited pages found."

        # For each unvisited page, run the one-page spider
        for page_url in unvisited_pages:
            cmd = (
                f"scrapy crawl one_page_spider -a page_url={page_url} "
                f"-a website_id={website_id} -a website_name='{website_name}'"
            )
            args = shlex.split(cmd)
            with open(output_file, "a") as f:
                result = subprocess.run(
                    args,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    env=env,
                    cwd=project_root
                )
                if result.returncode != 0:
                    raise Exception(f"Spider failed for URL {page_url}. See log: {output_file}")
        sleep(5)



























# import shlex
# import subprocess
# import os
# from celery import shared_task

# @shared_task
# def run_spider(website_id, website_name):
#     env = os.environ.copy()
#     env['SCRAPY_SETTINGS_MODULE'] = 'competitors_scraper.settings'
    
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     project_root = os.path.join(BASE_DIR, 'competitors_scraper')
#     env['PYTHONPATH'] = BASE_DIR + os.pathsep + env.get('PYTHONPATH', '')
    
#     cmd = f"scrapy crawl full_site_spider -a website_id={website_id} -a website_name='{website_name}'"
#     args = shlex.split(cmd)
    
#     # Redirect output to a file
#     output_file = os.path.join(project_root, 'spider_output.txt')
#     with open(output_file, "w") as f:
#         result = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=project_root)
    
#     if result.returncode != 0:
#         raise Exception(f"Spider process failed, see log at {output_file}")
    
#     return f"Spider output logged to {output_file}"














