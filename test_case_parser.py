from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TestCase:
    """Test case structure with all metadata"""
    id: str
    title: str
    customer_type: str  # RESI or BUSI
    customer_status: str  # new or existing  
    scenario_type: str  # install or cos
    truck_roll_type: str  # No or With
    content: str
    steps: List[Dict[str, str]]
    context: Dict = None
    is_generated: bool = False
    template_sources: List[str] = field(default_factory=list)
    generation_reasoning: str = None

@dataclass
class TestCaseRequirement:
    """Requirement for a test case type"""
    customer_type: str
    scenario_type: str
    truck_roll_type: str
    count_needed: int = 1
    priority: str = "medium"


import os
import sys
import re
from typing import List, Dict
from pathlib import Path

# Add the correct path to import RAG_context
sys.path.append(r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator")
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
        return 'No' if 'no truck' in filename.lower() else 'With'
    
    def _parse_steps(self, content: str) -> List[Dict[str, str]]:
        """Parse steps from content"""
        lines = content.split('\n')
        steps = []
        current_step = {}
        
        step_pattern = r'^(\d+)\.\s*(.+)'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            step_match = re.match(step_pattern, line)
            if step_match:
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    'step_number': step_match.group(1),
                    'action': step_match.group(2),
                    'expected_result': ''
                }
            elif 'expected result' in line.lower() and current_step:
                result = line.replace('Expected result', '').replace('Expected Result', '').strip()
                current_step['expected_result'] = result
        
        if current_step:
            steps.append(current_step)
        
        return steps
