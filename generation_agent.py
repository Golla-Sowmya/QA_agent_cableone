from typing import List, Optional
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from test_case_parser import TestCase, TestCaseRequirement
from test_case_schema import GeneratedTestCase, TestCaseStep

class GenerationAgent:
    """Simplified Generation Agent using GPT with Pydantic structured output"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context=None):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        
        # Create Pydantic output parser
        self.output_parser = PydanticOutputParser(pydantic_object=GeneratedTestCase)
        
        # Simple generation prompt for GPT
        self.generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert test case generator. Your job is to create test cases by copying and adapting existing templates.

IMPORTANT RULES:
1. Copy ALL steps from the template - never skip or reduce steps
2. Keep the exact same format and structure as the template
3. Only change these specific items:
   - Customer type references (Residential vs Commercial/Business)
   - Service codes (RESI uses HE008/HE009/HE015, BUSI uses BHSY5/BHSY6)
   - Test case name to match the target requirements

SERVICE CODE MAPPING (use prompts, no hardcoding):
- RESI customers: HE008 (Eero), HE009 (Eero Plus), HE015 (Eero Secure Plus) 
- BUSI CoS: BHSY5 (Eero W2W), BHSY6 (Eero Additional)

CRITICAL DEVICE REMOVAL SCENARIOS (High Priority for BUSI CoS):
When generating BUSI CoS test cases, prioritize these missing device management scenarios for customers with MULTIPLE Eero devices:
1. ID 29: Customer with Eero + ADDITIONAL Eero devices removing device (gateway No) 
2. ID 30: Customer with Eero + ADDITIONAL Eero devices removing device (gateway Yes)
3. ID 31: Customer with Eero + ADDITIONAL Eero devices removing entire Eero service + devices

IMPORTANT: These scenarios are for customers who have "existing_hsd_eero_additional" status - meaning they have multiple Eero devices in their setup, not just basic single Eero service.

Generate test cases that reflect complex multi-device environments with proper gateway distinction.

STEP FORMAT:
Each step should have:
- step_number: sequential number (1, 2, 3, etc.)
- content: complete step text including prerequisites, actions, and verifications

{format_instructions}"""),
            
            ("human", """Template to adapt:
{template_content}

Requirements:
- Customer Type: {customer_type}
- Scenario: {scenario_type} 
- Truck Roll: {truck_roll_type}
- Service Code: {service_code}

CRITICAL: Exact Combination Required:
{exact_combination_description}

IMPORTANT: If an exact combination description is provided above, you MUST adapt the template to match that PRECISE scenario. This includes:
- Adapting customer prerequisites to match the exact customer status (e.g., "existing_hsd_eero_additional")  
- Ensuring the test case reflects the specific business requirements and device management scenarios
- Modifying test case names and descriptions to match the exact combination needed

Please copy this template exactly, but adapt it for the requirements above. 
Change only the customer type references, service codes, and specific scenario details to match the exact combination.
Keep ALL steps and their detailed content.

Generate the test case now:""")
        ])
    
    async def generate_test_case(self, requirement: TestCaseRequirement, user_story: str) -> Optional[TestCase]:
        """Generate a test case using template adaptation"""
        print(f"    Generating test case for {requirement.customer_type} {requirement.scenario_type}...")
        
        # Find the best template to adapt
        template = self._find_best_template(requirement)
        if not template:
            print("    No suitable template found")
            return None
        
        step_count = len(template.steps) if template.steps else 0
        print(f"    Using template: {template.id} with {step_count} steps")
        
        # Determine service code using simple logic
        service_code = self._get_service_code(requirement)
        
        try:
            # Create the chain
            chain = self.generation_prompt | self.llm | self.output_parser
            
            # Generate the test case with exact combination description for precise adaptation
            exact_description = getattr(requirement, 'exact_combination_description', '')
            generated_case = await chain.ainvoke({
                "template_content": template.content,
                "customer_type": requirement.customer_type,
                "scenario_type": requirement.scenario_type,
                "truck_roll_type": requirement.truck_roll_type,
                "service_code": service_code,
                "exact_combination_description": exact_description,
                "format_instructions": self.output_parser.get_format_instructions()
            })
            
            # Convert to TestCase format
            test_case = self._convert_to_test_case(generated_case, requirement, template)
            step_count = len(test_case.steps) if test_case.steps else 0
            print(f"    Generated test case: {test_case.id} with {step_count} steps")
            return test_case
            
        except Exception as e:
            print(f"    Generation failed: {e}")
            return None
    
    def _find_best_template(self, requirement: TestCaseRequirement) -> Optional[TestCase]:
        """Find the best template to adapt - skip empty/corrupted files"""
        # Find exact matches first - exclude empty files
        exact_matches = [
            tc for tc in self.test_cases
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated and
                len(tc.steps) > 0 and  # Must have steps
                tc.content and len(tc.content.strip()) > 20)  # Must have substantial content
        ]
        
        if exact_matches:
            # Return the one with most steps (most detailed)
            best = max(exact_matches, key=lambda tc: len(tc.steps))
            print(f"    Found exact template match: {best.id} with {len(best.steps)} steps")
            return best
        
        # Fallback: find similar customer type and scenario - exclude empty files
        similar_matches = [
            tc for tc in self.test_cases
            if (tc.scenario_type == requirement.scenario_type and
                not tc.is_generated and
                not tc.id.startswith('TC_GEN_') and  # Avoid using generated templates
                len(tc.steps) > 0 and  # Must have steps
                tc.content and len(tc.content.strip()) > 20)  # Must have substantial content
        ]
        
        if similar_matches:
            best = max(similar_matches, key=lambda tc: len(tc.steps))
            print(f"    Found similar template: {best.id} with {len(best.steps)} steps")
            return best
        
        # Last resort: any good template with substantial content
        any_good_template = [
            tc for tc in self.test_cases
            if (not tc.is_generated and
                not tc.id.startswith('TC_GEN_') and
                len(tc.steps) > 5 and  # At least 5 steps
                tc.content and len(tc.content.strip()) > 50)  # Substantial content
        ]
        
        if any_good_template:
            best = max(any_good_template, key=lambda tc: len(tc.steps))
            print(f"    Using fallback template: {best.id} with {len(best.steps)} steps")
            return best
        
        print(f"    No suitable templates found")
        return None
    
    def _get_service_code(self, requirement: TestCaseRequirement) -> str:
        """Simple service code determination"""
        if requirement.customer_type == 'RESI':
            return 'HE008'  # Default to basic Eero for RESI
        else:  # BUSI
            if requirement.scenario_type == 'cos':
                return 'BHSY5'  # Eero W2W for BUSI CoS
            else:
                return 'BHSY1'  # Basic business install
    
    def _are_scenarios_equivalent(self, title1: str, title2: str) -> bool:
        """Check if two scenarios are equivalent (inline service matching)"""
        title1_lower = title1.lower()
        title2_lower = title2.lower()
        
        # Basic eero variations
        basic_variants = ['basic', 'eero', 'standard', 'hsd along with eero', 'he008']
        plus_variants = ['plus', 'eero plus', 'premium', 'he009']
        
        # Check if both are basic eero variants
        title1_basic = any(variant in title1_lower for variant in basic_variants)
        title2_basic = any(variant in title2_lower for variant in basic_variants)
        
        title1_plus = any(variant in title1_lower for variant in plus_variants)
        title2_plus = any(variant in title2_lower for variant in plus_variants)
        
        # They're equivalent if they're both basic or both plus
        return (title1_basic and title2_basic) or (title1_plus and title2_plus)
    
    def _convert_to_test_case(self, generated_case: GeneratedTestCase, 
                            requirement: TestCaseRequirement, template: TestCase) -> TestCase:
        """Convert Pydantic model to TestCase format"""
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_id = f"TC_GEN_{requirement.customer_type}_{requirement.scenario_type}_{timestamp}"
        
        # Convert steps to the format expected by TestCase
        steps = []
        for step in generated_case.test_steps:
            steps.append({
                'step_number': str(step.step_number),
                'action': step.content,
                'expected_result': ''
            })
        
        # Determine customer status
        customer_status = 'new' if requirement.scenario_type == 'install' else 'existing'
        
        return TestCase(
            id=test_id,
            title=generated_case.testcase_name,
            customer_type=requirement.customer_type,
            customer_status=customer_status,
            scenario_type=requirement.scenario_type,
            truck_roll_type=requirement.truck_roll_type,
            content=generated_case.to_file_format(),
            steps=steps,
            is_generated=True,
            template_sources=[template.id],
            generation_reasoning=f"Generated from template {template.id} for {requirement.customer_type} {requirement.scenario_type} scenario"
        )