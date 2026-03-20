import os
from pathlib import Path

# The project blueprint
structure = {
    ".env": "# Using asyncpg driver for async SQLAlchemy\nDATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/receipt_tracker_db\n",
    "requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\nasyncpg\npydantic\npydantic-settings\npython-dotenv\n",
    "app": {
        "__init__.py": "",
        "database.py": "# Paste the database.py code from our chat here!\n",
        "models.py": "# Paste the models.py code from our chat here!\n",
        "main.py": """from fastapi import FastAPI

app = FastAPI(title="Smart Receipt Scanner API")

@app.get("/")
async def root():
    return {"message": "API is up and running!"}
"""
    }
}

def build_structure(base_path: Path, node: dict):
    for name, content in node.items():
        path = base_path / name
        if isinstance(content, dict):
            # It's a folder
            path.mkdir(exist_ok=True)
            print(f"📁 Created directory: {path.relative_to(base_path)}")
            # Recursively build inside the folder
            build_structure(path, content)
        else:
            # It's a file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📄 Created file: {path.relative_to(base_path)}")

if __name__ == "__main__":
    current_dir = Path.cwd()
    print("🚀 Bootstrapping FastAPI project structure...\n")
    build_structure(current_dir, structure)
    print("\n✅ Done! You can safely delete this setup_project.py file now.")