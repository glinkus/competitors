Marketing analytics and competitor analysis platform. It provides tools for website analysis, SEO insights, keyword tracking, and reporting to help businesses be competitive in the market.

## Features

- Website and page-level SEO analysis
- Keyword tracking and analysis
- Competitor scraping and comparison
- Readability and content quality metrics
- Technology stack and audience insights
- PDF report generation

## Project Structure

- `dev/rarea/` — Restricted area frontend (JS, CSS)
- `dev/modules/analysis/` — Analysis modules (JS, templates)
- `dev/modules/competitors_scraper/` — Website scraping tools and logs

## Getting Started

### Prerequisites

- Node.js
- Python 3.13.2
- Django
- npm/yarn

### 1. Install dependencies
#### JavaScript
Run the following command to install the required dependencies:
```sh
npm ci
```
#### Python
Set up a virtual environment and install the necessary packages:
```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize the database
Create migration files and apply them to set up the database tables:
```sh
python dev/manage.py makemigrations
python dev/manage.py migrate
```

### 3. Create a default user
Create an admin user to log in to the system. Replace `<name>` with an appropriate value:
```sh
DJANGO_SUPERUSER_PASSWORD="Secret#Web#Dev" python dev/manage.py createsuperuser --no-input --username gustas --email gustas@dev.indeform.com
```

## Development
### Start development servers
1. Start the Webpack bundler to compile front-end assets and watch for changes:
    ```sh
    npm run dev
    ```
2. Start the Django development server:
    ```sh
    python dev/manage.py runserver
    ```
    To run the server with a debugger ([debugpy](https://github.com/microsoft/debugpy)) support:
    ```
    python -Xfrozen_modules=off -m debugpy --listen localhost:5678 dev/manage.py runserver
    ```
    * **VS Code users:** To use a debugger through the IDE, put the configuration below into `.vscode/launch.json`. Then start the Django web  server as described above, open "Run and Debug" tab and run "Attach to Django" task which will connect to the debugger server.
    ```
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Attach to Django",
                "type": "debugpy",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 5678
                },
                "justMyCode": true
            }
        ]
    }
    ```
3. Start background process Celery:
    ```sh
    cd dev && celery -A main worker -l info
    ```

### Recommended versions
The project is known to work with the following versions:
```
NodeJS: v22.11.0
NPM: 10.9.0
Python: 3.13.2
Pip: 25.0.1
```

### Usage

- Access the dashboard to add websites for analysis.
- View SEO, keyword, and competitor analysis insights.
- Generate and download PDF reports.

