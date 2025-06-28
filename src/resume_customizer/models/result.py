# ABOUTME: CustomizationResult model for tracking resume customization changes
# ABOUTME: Provides change tracking, diff generation, and various export formats

"""Models for tracking and representing resume customization results."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
import json
import difflib
from pathlib import Path


class ChangeType(str, Enum):
    """Types of changes that can be made during customization."""
    CONTENT_REWRITE = "content_rewrite"
    KEYWORD_ADDITION = "keyword_addition"
    SECTION_REORDER = "section_reorder"
    FORMAT_UPDATE = "format_update"
    SECTION_EMPHASIS = "section_emphasis"


class DiffType(str, Enum):
    """Types of differences in diff output."""
    ADDED = "added"
    REMOVED = "removed"
    UNCHANGED = "unchanged"


@dataclass
class Change:
    """Represents a single change made during customization."""
    type: ChangeType
    section: str
    description: str


@dataclass
class SectionChange:
    """Represents a section reordering change."""
    original_position: int
    new_position: int
    section_name: str


@dataclass
class KeywordIntegration:
    """Represents keyword integration details."""
    keyword: str
    frequency: int
    sections: List[str]


@dataclass
class DiffLine:
    """Represents a line in the diff output."""
    type: DiffType
    content: str
    line_num: int


@dataclass
class CustomizationResult:
    """
    Comprehensive result of resume customization process.
    
    Tracks all changes made, keywords integrated, sections reordered,
    and provides various export and analysis methods.
    """
    original_content: str
    customized_content: str
    match_score: float
    changes: List[Change]
    integrated_keywords: List[str]
    reordered_sections: List[SectionChange]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not 0 <= self.match_score <= 100:
            raise ValueError("Match score must be between 0 and 100")
    
    def get_change_summary(self) -> str:
        """Generate a concise summary of changes made."""
        if not self.changes and not self.integrated_keywords and not self.reordered_sections:
            return "No changes made"
        
        lines = [
            f"Match Score: {self.match_score}%",
            f"Total Changes: {len(self.changes)}",
            f"Keywords Added: {len(self.integrated_keywords)}",
            f"Sections Reordered: {len(self.reordered_sections)}",
            ""
        ]
        
        if self.changes:
            lines.append("Changes by Section:")
            for change in self.changes:
                lines.append(f"  - {change.section}: {change.description}")
        
        return "\n".join(lines)
    
    def get_detailed_summary(self) -> str:
        """Generate a detailed summary with all information."""
        lines = [
            "=" * 50,
            "RESUME CUSTOMIZATION SUMMARY",
            "=" * 50,
            f"Generated at: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Match Score: {self.match_score}%",
            "",
        ]
        
        # Changes section
        if self.changes:
            lines.extend([
                "Changes Applied:",
                "-" * 30,
            ])
            for i, change in enumerate(self.changes, 1):
                lines.append(f"{i}. [{change.type.value}] {change.section}")
                lines.append(f"   {change.description}")
                lines.append("")
        
        # Keywords section
        if self.integrated_keywords:
            lines.extend([
                "Integrated Keywords:",
                "-" * 30,
            ])
            for keyword in self.integrated_keywords:
                lines.append(f"  - {keyword}")
            lines.append("")
        
        # Section reordering
        if self.reordered_sections:
            lines.extend([
                "Section Order Changes:",
                "-" * 30,
            ])
            for section in self.reordered_sections:
                lines.append(
                    f"  - {section.section_name} moved from position "
                    f"{section.original_position} to position {section.new_position}"
                )
        
        return "\n".join(lines)
    
    def get_keyword_frequency(self) -> Dict[str, int]:
        """Analyze keyword frequency in the customized content."""
        freq = {}
        content_lower = self.customized_content.lower()
        
        for keyword in self.integrated_keywords:
            keyword_lower = keyword.lower()
            # Count whole word occurrences
            count = content_lower.count(keyword_lower)
            if count > 0:
                freq[keyword] = count
        
        return freq
    
    def generate_diff(self) -> List[DiffLine]:
        """Generate a diff between original and customized content."""
        original_lines = self.original_content.splitlines()
        customized_lines = self.customized_content.splitlines()
        
        diff_lines = []
        original_line_num = 0
        customized_line_num = 0
        
        differ = difflib.Differ()
        diff = list(differ.compare(original_lines, customized_lines))
        
        for line in diff:
            if line.startswith('  '):  # Unchanged
                original_line_num += 1
                customized_line_num += 1
                diff_lines.append(
                    DiffLine(
                        type=DiffType.UNCHANGED,
                        content=line[2:],
                        line_num=original_line_num
                    )
                )
            elif line.startswith('- '):  # Removed
                original_line_num += 1
                diff_lines.append(
                    DiffLine(
                        type=DiffType.REMOVED,
                        content=line[2:],
                        line_num=original_line_num
                    )
                )
            elif line.startswith('+ '):  # Added
                customized_line_num += 1
                diff_lines.append(
                    DiffLine(
                        type=DiffType.ADDED,
                        content=line[2:],
                        line_num=customized_line_num
                    )
                )
            # Skip '?' lines from differ
        
        return diff_lines
    
    def format_for_cli(self) -> str:
        """Format the result for CLI output with colors and symbols."""
        # ANSI color codes
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        lines = [
            f"{BOLD}Resume Customization Complete!{RESET}",
            "",
            f"{GREEN}✓ Match Score: {self.match_score}%{RESET}",
            "",
            f"{BLUE}Changes Applied:{RESET}",
        ]
        
        for change in self.changes:
            lines.append(f"  {GREEN}✓{RESET} {change.section}: {change.description}")
        
        if self.integrated_keywords:
            lines.extend([
                "",
                f"{BLUE}Keywords Integrated:{RESET}",
                f"  {YELLOW}{', '.join(self.integrated_keywords)}{RESET}"
            ])
        
        if self.reordered_sections:
            lines.extend([
                "",
                f"{BLUE}Sections Reordered:{RESET}",
            ])
            for section in self.reordered_sections:
                lines.append(
                    f"  {GREEN}↕{RESET} {section.section_name} "
                    f"({section.original_position} → {section.new_position})"
                )
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert the result to a dictionary."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data['timestamp'] = self.timestamp.isoformat()
        # Convert enums to strings
        for change in data['changes']:
            change['type'] = change['type']
        return data
    
    def to_json(self) -> str:
        """Convert the result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """Save the result to a JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(self.to_json())
    
    def calculate_improvement_percentage(self, original_keywords: int) -> float:
        """Calculate the percentage improvement in keyword coverage."""
        if original_keywords == 0:
            return 100.0 if self.integrated_keywords else 0.0
        
        new_keywords = len(self.integrated_keywords)
        improvement = ((new_keywords - original_keywords) / original_keywords) * 100
        return max(0.0, improvement)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistical summary of the customization."""
        stats = {
            "total_changes": len(self.changes),
            "keywords_added": len(self.integrated_keywords),
            "sections_reordered": len(self.reordered_sections),
            "match_score": self.match_score,
        }
        
        # Count changes by type
        for change_type in ChangeType:
            count = sum(1 for c in self.changes if c.type == change_type)
            stats[f"{change_type.value}_count"] = count
        
        return stats
    
    def export_as_markdown(self) -> str:
        """Export the result summary as markdown."""
        lines = [
            "# Resume Customization Report",
            "",
            f"**Generated**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"## Match Score: {self.match_score}%",
            "",
        ]
        
        if self.changes:
            lines.extend([
                "### Changes Applied",
                "",
            ])
            for change in self.changes:
                lines.append(f"- **{change.section}**: {change.description}")
            lines.append("")
        
        if self.integrated_keywords:
            lines.extend([
                "### Integrated Keywords",
                "",
            ])
            for keyword in self.integrated_keywords:
                lines.append(f"- {keyword}")
            lines.append("")
        
        if self.reordered_sections:
            lines.extend([
                "### Section Reordering",
                "",
            ])
            for section in self.reordered_sections:
                lines.append(
                    f"- **{section.section_name}**: Position {section.original_position} → {section.new_position}"
                )
        
        return "\n".join(lines)
    
    def get_comparison_metrics(self) -> Dict[str, float]:
        """Generate metrics comparing original and customized content."""
        original_length = len(self.original_content)
        customized_length = len(self.customized_content)
        
        # Basic metrics
        metrics = {
            "original_length": original_length,
            "customized_length": customized_length,
            "length_increase_percent": (
                ((customized_length - original_length) / original_length * 100)
                if original_length > 0 else 0
            ),
        }
        
        # Keyword density
        original_keywords = sum(
            self.original_content.lower().count(kw.lower())
            for kw in self.integrated_keywords
        )
        customized_keywords = sum(
            self.customized_content.lower().count(kw.lower())
            for kw in self.integrated_keywords
        )
        
        metrics["keyword_density_change"] = customized_keywords - original_keywords
        
        return metrics