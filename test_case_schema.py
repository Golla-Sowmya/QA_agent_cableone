from typing import List, Optional
from pydantic import BaseModel, Field

class TestCaseStep(BaseModel):
    """Individual test step matching exact format from test case files"""
    step_number: int = Field(description="Step number (1, 2, 3, etc.)")
    content: str = Field(description="Complete step content including actions and verifications")

class GeneratedTestCase(BaseModel):
    """Complete test case matching exact format from test case folder"""
    testcase_name: str = Field(
        description="Test case name in format: RESI/BUSI - Install/CoS - Description - Truck Roll type",
        examples=["BUSI - Install HSD along with Eero - No TruckRoll"]
    )
    test_steps: List[TestCaseStep] = Field(
        description="All test steps in exact format from template",
        min_items=1
    )
    
    def to_file_format(self) -> str:
        """Convert to exact file format matching test case folder"""
        content = f"Testcase_name: {self.testcase_name}\n"
        content += "Test_steps:\n"
        
        for step in self.test_steps:
            content += f"{step.step_number}.\n"
            content += f"{step.content}\n"
        
        return content
    
    class Config:
        json_schema_extra = {
            "example": {
                "testcase_name": "RESI - Install HSD along with Eero - With TruckRoll",
                "test_steps": [
                    {
                        "step_number": 1,
                        "content": "Prerequisite:\nThe test tech inventory includes an HSD and Eero devices..."
                    },
                    {
                        "step_number": 2, 
                        "content": "From the Common Search window:\n- Select customer type: Residential;\n- Enter the primary phone number..."
                    }
                ]
            }
        }