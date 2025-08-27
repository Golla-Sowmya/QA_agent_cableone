from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TestCase(BaseModel):
    """Test case structure with all metadata"""
    id: str
    title: str
    customer_type: str  # RESI or BUSI
    customer_status: str  # new or existing  
    scenario_type: str  # install or cos
    truck_roll_type: str  # No or With
    content: str
    steps: List[Dict[str, str]]
    context: Optional[Dict] = None
    is_generated: bool = False
    template_sources: List[str] = Field(default_factory=list)
    generation_reasoning: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        extra = "allow"  # Allow additional fields for flexibility

class TestCaseRequirement(BaseModel):
    """Requirement for a test case type"""
    customer_type: str
    scenario_type: str
    truck_roll_type: str
    count_needed: int = 1
    priority: str = "medium"
    
    class Config:
        """Pydantic configuration"""
        extra = "allow"  # Allow additional fields for flexibility


import os
import sys
import re
from typing import List, Dict
from pathlib import Path

# Add the correct path to import RAG_context
sys.path.append(r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator")
# sys.path.append(r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator\test_cases")
from RAG_context import TestCaseRAGContext

class TestCaseParser:
    """Parse test cases from files with RAG context integration"""
    
    def __init__(self):
        self.rag_context = TestCaseRAGContext()
    
    def parse_from_file(self, file_path: str) -> List[TestCase]:
        """Parse test case from file with RAG context"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []
        
        filename = Path(file_path).name
        filename_stem = Path(file_path).stem
        
        # Extract info from filename pattern
        customer_type = self._extract_customer_type(filename_stem)
        scenario_type = self._extract_scenario_type(filename_stem)
        truck_roll_type = self._extract_truck_roll_type(filename_stem)
        
        customer_status = 'existing' if scenario_type == 'cos' else 'new'
        steps = self._parse_steps(content)
        context = self._get_rag_context_for_file(filename)
        
        test_case = TestCase(
            id=f"TC_{filename_stem}",
            title=filename_stem.replace('_', ' ').replace('-', ' ').strip(),
            customer_type=customer_type,
            customer_status=customer_status,
            scenario_type=scenario_type,
            truck_roll_type=truck_roll_type,
            content=content,
            steps=steps,
            context=context
        )
        
        return [test_case]
    
    def _get_rag_context_for_file(self, filename: str) -> Dict:
        """Get RAG context for specific test case file"""
        for chunk in self.rag_context.chunks:
            chunk_filename = chunk.get('file_name') or chunk.get('test_case_name') or ''
            if chunk_filename.lower() == filename.lower():
                return chunk
        
        # Partial match fallback
        for chunk in self.rag_context.chunks:
            chunk_filename = chunk.get('file_name') or chunk.get('test_case_name') or ''
            chunk_name = chunk_filename.lower().replace('.txt', '')
            file_name = filename.lower().replace('.txt', '')
            if chunk_name and (chunk_name in file_name or file_name in chunk_name):
                return chunk
        
        return None
    
    def _extract_customer_type(self, filename: str) -> str:
        """Extract RESI or BUSI from filename"""
        return 'RESI' if 'RESI' in filename.upper() else 'BUSI'
    
    def _extract_scenario_type(self, filename: str) -> str:
        """Extract Install or CoS from filename"""
        return 'cos' if 'cos' in filename.lower() else 'install'
    
    def _extract_truck_roll_type(self, filename: str) -> str:
        """Extract truck roll type from filename"""
        filename_lower = filename.lower()
        
        # Check for explicit "No" truck roll patterns
        if any(pattern in filename_lower for pattern in ['no truckroll', 'no truck roll']):
            return 'No'
        
        # Check for explicit "With" truck roll patterns  
        if any(pattern in filename_lower for pattern in ['with truckroll', 'with truck roll', 'w truck roll']):
            return 'With'
        
        # For CoS scenarios without explicit truck roll indication, default to 'No'
        # For Install scenarios without explicit truck roll indication, default to 'With'
        if 'cos' in filename_lower:
            return 'No'
        else:
            return 'With'
    
    def _parse_steps(self, content: str) -> List[Dict[str, str]]:
        """Parse steps from content with comprehensive step extraction"""
        lines = content.split('\n')
        steps = []
        current_step = {}
        in_test_steps = False
        
        # Enhanced step patterns
        step_patterns = [
            r'^(\d+)\.\s*$',  # Step number alone on a line
            r'^(\d+)\.\s*(.+)',  # Step number with content
            r'^\s*(\d+)\s*\.\s*(.+)',  # Step with possible leading spaces
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip to Test_steps section
            if 'Test_steps:' in line:
                in_test_steps = True
                i += 1
                continue
            
            if not in_test_steps or not line:
                i += 1
                continue
            
            # Check for step pattern
            step_found = False
            for pattern in step_patterns:
                step_match = re.match(pattern, line)
                if step_match:
                    # Save previous step if exists
                    if current_step and current_step.get('action'):
                        steps.append(current_step)
                    
                    step_number = step_match.group(1)
                    step_content = step_match.group(2) if len(step_match.groups()) > 1 else ""
                    
                    # Collect all content for this step
                    step_lines = []
                    if step_content:
                        step_lines.append(step_content)
                    
                    # Look ahead to collect all lines until next step
                    j = i + 1
                    collected_lines = 0  # Safety counter to prevent infinite loops
                    max_lines_per_step = 50  # Maximum lines to collect for one step
                    
                    while j < len(lines) and collected_lines < max_lines_per_step:
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        # Check if this is the next step
                        is_next_step = False
                        for check_pattern in step_patterns:
                            if re.match(check_pattern, next_line):
                                is_next_step = True
                                break
                        
                        if is_next_step:
                            break
                        else:
                            step_lines.append(next_line)
                            j += 1
                            collected_lines += 1
                    
                    # Create step object
                    full_action = ' '.join(step_lines).strip()
                    
                    # Extract expected results if present
                    expected_result = ""
                    if any(keyword in full_action.lower() for keyword in [
                        'verify', 'check', 'ensure', 'confirm', 'validate'
                    ]):
                        # Try to extract verification parts as expected results
                        verify_patterns = [
                            r'verify\s+(.+?)(?:\.|$)',
                            r'check\s+(.+?)(?:\.|$)',
                            r'ensure\s+(.+?)(?:\.|$)',
                            r'confirm\s+(.+?)(?:\.|$)',
                            r'validate\s+(.+?)(?:\.|$)'
                        ]
                        for vpattern in verify_patterns:
                            verify_match = re.search(vpattern, full_action.lower())
                            if verify_match:
                                expected_result = verify_match.group(1).strip()
                                break
                    
                    current_step = {
                        'step_number': step_number,
                        'action': full_action,
                        'expected_result': expected_result
                    }
                    
                    step_found = True
                    i = j  # Set i to continue from where we left off
                    break
            
            if not step_found:
                i += 1
        
        # Don't forget the last step
        if current_step and current_step.get('action'):
            steps.append(current_step)
        
        return steps
