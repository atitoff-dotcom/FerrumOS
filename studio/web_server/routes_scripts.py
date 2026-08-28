import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
from .models import ScriptSaveRequest

router = APIRouter(prefix="/api/scripts", tags=["scripts"])

def extract_first_comment(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("//") or line.startswith("/*") or line.startswith("*") or line.startswith("#"):
                cleaned = re.sub(r"^(\/\/|\/\*|\*|#)+", "", line).rstrip("*/").strip()
                if cleaned and not re.match(r"^[=\-_*#]{3,}$", cleaned):
                    return cleaned
            elif line:
                break
    except Exception:
        pass
    return ""

@router.get("")
@router.get("/")
def list_scripts():
    scripts_dir = Path("scripts")
    items = {}
    if scripts_dir.exists():
        for f in scripts_dir.glob("*.js"):
            items[f.name] = {
                "filename": f.name,
                "description": extract_first_comment(f),
                "size": f.stat().st_size,
            }
    for node_dir in Path("storage/nodes").glob("*"):
        for script_file in (node_dir / "current").glob("*.js"):
            if script_file.name not in items:
                items[script_file.name] = {
                    "filename": script_file.name,
                    "description": extract_first_comment(script_file),
                    "size": script_file.stat().st_size,
                }
    return sorted(items.values(), key=lambda x: x["filename"])

@router.get("/{filename}")
def read_script(filename: str):
    path = Path("scripts") / filename
    if not path.exists():
        for node_dir in Path("storage/nodes").glob("*"):
            node_file = node_dir / "current" / filename
            if node_file.exists():
                return {"filename": filename, "code": node_file.read_text(encoding="utf-8")}
        raise HTTPException(status_code=404, detail="Script not found")
    return {"filename": filename, "code": path.read_text(encoding="utf-8")}

@router.post("/{filename}")
def save_script(filename: str, req: ScriptSaveRequest):
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    path = scripts_dir / filename
    path.write_text(req.code, encoding="utf-8")
    return {"status": "ok", "filename": filename}

@router.delete("/{filename}")
def delete_script(filename: str):
    path = Path("scripts") / filename
    if path.exists():
        path.unlink()
        return {"status": "ok", "deleted": filename}
    for node_dir in Path("storage/nodes").glob("*"):
        node_file = node_dir / "current" / filename
        if node_file.exists():
            node_file.unlink()
            return {"status": "ok", "deleted": filename}
    raise HTTPException(status_code=404, detail="File not found")
