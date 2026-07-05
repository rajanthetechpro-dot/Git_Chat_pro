import os
import re
from typing import Dict, Any, List, Tuple

class CodebaseAnalyzer:
    @staticmethod
    def analyze_repository(local_dir: str) -> Dict[str, Any]:
        """
        Scans a local repository directory to generate rich statistics and static analysis metrics.
        """
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "languages": {},       # e.g., {".py": {"files": 5, "lines": 450}}
            "todos": [],           # List of dicts: {"file": "...", "line": 42, "content": "..."}
            "security_alerts": [],  # List of dicts: {"file": "...", "line": 12, "issue": "...", "severity": "..."}
            "large_files": []      # List of tuples: (file_path, size_bytes)
        }

        # Regex for potential secrets and credentials
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret|password|passwd|token|private[_-]?key)\s*=\s*[\'"][a-zA-Z0-9_\-\.\=\+]{16,}[\'"]', "Hardcoded Secret/Token (High)"),
            (r'(?i)(db_password|database_password|db_pass)\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Database Password (High)"),
            (r'eval\s*\(\s*[^)]+\s*\)', "Usage of eval() (Medium/Low)"),
            (r'subprocess\s*\.\s*(run|Popen|call)\s*\(\s*[^,]+,\s*shell\s*=\s*True\s*\)', "Subprocess with shell=True (Medium)")
        ]

        todo_pattern = re.compile(r'\b(TODO|FIXME|BUG|HACK)\b', re.IGNORECASE)

        for root, dirs, files in os.walk(local_dir):
            # Skip hidden folders like .git, .cache
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, local_dir)
                
                # Exclude massive files or binary files
                try:
                    size = os.path.getsize(file_path)
                except OSError:
                    continue
                
                # Check for large files
                stats["large_files"].append((rel_path, size))
                
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    ext = "No Extension"
                
                stats["total_files"] += 1
                
                if ext not in stats["languages"]:
                    stats["languages"][ext] = {"files": 0, "lines": 0}
                stats["languages"][ext]["files"] += 1
                
                # Read text files for line-level analysis
                # We skip files larger than 2MB to prevent lockups
                if size > 2 * 1024 * 1024:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                except Exception:
                    # Ignore unreadable/binary files
                    continue
                
                file_lines = len(lines)
                stats["total_lines"] += file_lines
                stats["languages"][ext]["lines"] += file_lines
                
                # Parse lines
                for idx, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # Detect blank lines
                    if not stripped:
                        stats["blank_lines"] += 1
                        continue
                    
                    # Detect comments
                    is_comment = False
                    if ext in [".py", ".sh", ".yaml", ".yml", ".toml", ".ini", ".conf"]:
                        if stripped.startswith("#"):
                            is_comment = True
                    elif ext in [".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".php"]:
                        if stripped.startswith("//") or stripped.startswith("/*") or stripped.endswith("*/"):
                            is_comment = True
                    elif ext in [".html", ".xml", ".md"]:
                        if stripped.startswith("<!--") or stripped.endswith("-->"):
                            is_comment = True
                    
                    if is_comment:
                        stats["comment_lines"] += 1
                    else:
                        stats["code_lines"] += 1
                    
                    # Search for TODOs/FIXMEs
                    if todo_pattern.search(line):
                        stats["todos"].append({
                            "file": rel_path,
                            "line": idx,
                            "content": stripped[:120]  # Limit length
                        })
                        
                    # Search for security threats
                    for pattern, issue_desc in secret_patterns:
                        if re.search(pattern, stripped):
                            severity = "High" if "High" in issue_desc else "Medium"
                            stats["security_alerts"].append({
                                "file": rel_path,
                                "line": idx,
                                "issue": issue_desc,
                                "severity": severity,
                                "content": stripped[:120]
                            })

        # Sort large files and keep top 10
        stats["large_files"].sort(key=lambda x: x[1], reverse=True)
        stats["large_files"] = stats["large_files"][:10]
        
        return stats
