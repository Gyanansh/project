# GitHub Repository Analyzer Backend

This is a Django REST Framework backend for analyzing GitHub repositories using AI and static analysis tools.

 es

- **Tree Visualizer**: Fetch repository structure (`/api/repo/tree/`).
- **File Analysis**: AI-powered explanation and vulnerability scanning (`/api/repo/analyze-file/`, `/api/repo/vulnerabilities/`).
- **Reports**: Generate structure and API reports (`/api/repo/report/`).
- **Roadmap**: Suggest improvements and roadmap (`/api/repo/roadmap/`).
- **Contribution**: Guides and good first issues (`/api/repo/contribution-guide/`).
- **PR Patterns**: Analyze pull request patterns (`/api/repo/pr-patterns/`).

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory (copy from `.env.example`) and set:
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token.
   - `REDIS_URL`: Redis URL (optional, defaults to local).

3. **Run Migrations**
   ```bash
   cd repo_analyzer
   python manage.py migrate
   ```

4. **Start Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

- **GET /api/repo/tree/?owner={owner}&repo={repo}**
- **GET /api/repo/analyze-file/?owner={owner}&repo={repo}&path={path}**
- **GET /api/repo/vulnerabilities/?owner={owner}&repo={repo}&path={path}**
- **GET /api/repo/report/?owner={owner}&repo={repo}**
- **GET /api/repo/roadmap/?owner={owner}&repo={repo}**
- **GET /api/repo/contribution-guide/?owner={owner}&repo={repo}**
- **GET /api/repo/pr-patterns/?owner={owner}&repo={repo}**

## Testing

Run tests using:
```bash
python manage.py test
```
