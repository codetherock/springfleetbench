"""Mechanical example candidate for the synthetic pilot tasks."""

import os
from pathlib import Path


repo = Path(os.environ["SFB_REPO_DIR"])
pom = repo / "pom.xml"
text = pom.read_text(encoding="utf-8")
text = text.replace("<version>2.7.18</version>", "<version>3.2.5</version>")
text = text.replace("<java.version>11</java.version>", "<java.version>17</java.version>")
pom.write_text(text, encoding="utf-8")

for java_file in (repo / "src/main/java").rglob("*.java"):
    source = java_file.read_text(encoding="utf-8")
    java_file.write_text(source.replace("javax.validation", "jakarta.validation"), encoding="utf-8")
