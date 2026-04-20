import json
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    entry_id: str
    field: str
    error_type: str
    message: str


class CorpusValidator:
    MANDATORY_FIELDS = {
        "id", "chapter", "verses", "sloka_sanskrit_iast", 
        "translation_english", "themes", "keywords"
    }
    
    OPTIONAL_FIELDS = {
        "context", "interpretive_notes", "supportive_practices", "image_tags"
    }
    
    VALID_SCOPES = {"descriptive", "ethical", "metaphysical", "devotional", "philosophical", "practical", "cosmic"}
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_corpus(self, corpus: List[Dict[str, Any]]) -> bool:
        self.errors.clear()
        self.warnings.clear()
        
        if not isinstance(corpus, list):
            self.errors.append(ValidationError(
                entry_id="CORPUS_ROOT",
                field="root",
                error_type="TYPE_ERROR",
                message="Corpus must be a list"
            ))
            return False
        
        seen_ids: Set[str] = set()
        
        for idx, entry in enumerate(corpus):
            entry_id = entry.get("id", f"ENTRY_{idx}")
            
            if entry_id in seen_ids:
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field="id",
                    error_type="DUPLICATE_ID",
                    message=f"Duplicate verse ID: {entry_id}"
                ))
            seen_ids.add(entry_id)
            
            self._validate_entry(entry, entry_id)
        
        return len(self.errors) == 0
    
    def _validate_entry(self, entry: Dict[str, Any], entry_id: str):
        for field in self.MANDATORY_FIELDS:
            if field not in entry:
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field=field,
                    error_type="MISSING_MANDATORY_FIELD",
                    message=f"Missing mandatory field: {field}"
                ))
        
        if "id" in entry and not isinstance(entry["id"], str):
            self.errors.append(ValidationError(
                entry_id=entry_id,
                field="id",
                error_type="TYPE_ERROR",
                message="Field 'id' must be a string"
            ))
        
        if "chapter" in entry and not isinstance(entry["chapter"], int):
            self.errors.append(ValidationError(
                entry_id=entry_id,
                field="chapter",
                error_type="TYPE_ERROR",
                message="Field 'chapter' must be an integer"
            ))
        
        if "verses" in entry:
            if not isinstance(entry["verses"], list):
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field="verses",
                    error_type="TYPE_ERROR",
                    message="Field 'verses' must be a list"
                ))
            elif not all(isinstance(v, int) for v in entry["verses"]):
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field="verses",
                    error_type="TYPE_ERROR",
                    message="All verse numbers must be integers"
                ))
        
        for field in ["sloka_sanskrit_iast", "translation_english"]:
            if field in entry and not isinstance(entry[field], str):
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field=field,
                    error_type="TYPE_ERROR",
                    message=f"Field '{field}' must be a string"
                ))
        
        for field in ["themes", "keywords"]:
            if field in entry:
                if not isinstance(entry[field], list):
                    self.errors.append(ValidationError(
                        entry_id=entry_id,
                        field=field,
                        error_type="TYPE_ERROR",
                        message=f"Field '{field}' must be a list"
                    ))
                elif not all(isinstance(item, str) for item in entry[field]):
                    self.errors.append(ValidationError(
                        entry_id=entry_id,
                        field=field,
                        error_type="TYPE_ERROR",
                        message=f"All items in '{field}' must be strings"
                    ))
        
        if "interpretive_notes" in entry:
            notes = entry["interpretive_notes"]
            if not isinstance(notes, dict):
                self.errors.append(ValidationError(
                    entry_id=entry_id,
                    field="interpretive_notes",
                    error_type="TYPE_ERROR",
                    message="Field 'interpretive_notes' must be a dictionary"
                ))
            else:
                if "scope" in notes and notes["scope"] not in self.VALID_SCOPES:
                    self.warnings.append(ValidationError(
                        entry_id=entry_id,
                        field="interpretive_notes.scope",
                        error_type="INVALID_VALUE",
                        message=f"Scope '{notes['scope']}' not in valid scopes: {self.VALID_SCOPES}"
                    ))
        
        all_fields = set(entry.keys())
        unknown_fields = all_fields - self.MANDATORY_FIELDS - self.OPTIONAL_FIELDS
        if unknown_fields and self.strict_mode:
            self.warnings.append(ValidationError(
                entry_id=entry_id,
                field=",".join(unknown_fields),
                error_type="UNKNOWN_FIELD",
                message=f"Unknown fields detected: {unknown_fields}"
            ))
    
    def get_validation_report(self) -> str:
        report = []
        report.append("=" * 80)
        report.append("CORPUS VALIDATION REPORT")
        report.append("=" * 80)
        
        if not self.errors and not self.warnings:
            report.append("✓ Corpus validation PASSED")
            report.append("  No errors or warnings detected")
        else:
            if self.errors:
                report.append(f"\n✗ ERRORS: {len(self.errors)}")
                for error in self.errors:
                    report.append(f"  [{error.entry_id}] {error.field}: {error.message}")
            
            if self.warnings:
                report.append(f"\n⚠ WARNINGS: {len(self.warnings)}")
                for warning in self.warnings:
                    report.append(f"  [{warning.entry_id}] {warning.field}: {warning.message}")
        
        report.append("=" * 80)
        return "\n".join(report)


class CorpusLoader:
    def __init__(self, corpus_path: str, strict_validation: bool = True):
        self.corpus_path = Path(corpus_path)
        self.validator = CorpusValidator(strict_mode=strict_validation)
        self.corpus: List[Dict[str, Any]] = []
        self.index: Dict[str, Dict[str, Any]] = {}
    
    def load(self) -> bool:
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}")
        
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        
        is_valid = self.validator.validate_corpus(self.corpus)
        
        print(self.validator.get_validation_report())
        
        if not is_valid:
            raise ValueError("Corpus validation failed. See report above.")
        
        self._build_index()
        
        return True
    
    def _build_index(self):
        self.index.clear()
        for verse in self.corpus:
            verse_id = verse["id"]
            self.index[verse_id] = verse
    
    def get_verse_by_id(self, verse_id: str) -> Optional[Dict[str, Any]]:
        return self.index.get(verse_id)
    
    def get_all_verses(self) -> List[Dict[str, Any]]:
        return self.corpus
    
    def get_verses_by_chapter(self, chapter: int) -> List[Dict[str, Any]]:
        return [v for v in self.corpus if v["chapter"] == chapter]
    
    def get_verses_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        return [v for v in self.corpus if theme in v.get("themes", [])]
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        total_verses = len(self.corpus)
        chapters = set(v["chapter"] for v in self.corpus)
        all_themes = set()
        all_keywords = set()
        
        for verse in self.corpus:
            all_themes.update(verse.get("themes", []))
            all_keywords.update(verse.get("keywords", []))
        
        return {
            "total_verses": total_verses,
            "chapters_covered": sorted(list(chapters)),
            "unique_themes": len(all_themes),
            "unique_keywords": len(all_keywords),
            "themes": sorted(list(all_themes)),
            "keywords": sorted(list(all_keywords))
        }
