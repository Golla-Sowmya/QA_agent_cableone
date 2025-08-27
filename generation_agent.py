import re
import uuid
import time
from typing import List, Dict, Optional, Set
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from test_case_parser import TestCase, TestCaseRequirement

class GeneratedTestCase(BaseModel):
    """Pydantic model for structured test case generation matching output format"""
    testcase_id: str = Field(description="Unique test case identifier like TC_GEN_RESI_cos_20250822")
    testcase_name: str = Field(description="Descriptive test case name")
    customer_type: str = Field(description="Customer type: RESI or BUSI")
    customer_status: str = Field(description="Customer status: new or existing")
    scenario_type: str = Field(description="Scenario type: install or cos")
    truck_roll_type: str = Field(description="Truck roll type: With or No")
    step_count: int = Field(description="Number of detailed steps in the test case")
    complete_steps: str = Field(description="Complete formatted test case content with all steps, prerequisites, and validations")

class GenerationAgent:
    """Enhanced Generation Agent with MANDATORY complete step preservation"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        self._generated_ids: Set[str] = set()  # Track generated IDs to prevent duplicates
        self._id_counter = 1  # Counter for uniqueness
        self._used_templates: Set[str] = set()  # Track recently used templates
        
        # Create Pydantic output parser for structured generation
        self.output_parser = PydanticOutputParser(pydantic_object=GeneratedTestCase)
        
        # Simplified generation prompt optimized for o1-mini
        self.generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a test case generator. Copy all steps from the template and adapt them.

Rules:
- Copy ALL steps from template (exactly {step_count} steps)
- Replace service codes: RESI uses HE008/HE009/HE015, BUSI uses BHSY1/BHSY2/BHSY3/BHSY5/BHSY6
- Update customer type references (Residential/Business)
- Keep all step details exactly as in template"""),
            
            ("human", """Template ({step_count} steps):
{template_content}

Adapt for: {customer_type} customer, {scenario_type} scenario, service code {service_code}, {truck_roll_type} truck roll

Generate test case with ALL {step_count} steps in this exact format:

testcase_id: [unique ID]
testcase_name: [descriptive name]
customer_type: {customer_type}
customer_status: {customer_status}
scenario_type: {scenario_type}
truck_roll_type: {truck_roll_type}
step_count: {step_count}
complete_steps: [copy all steps from template, replace service codes with {service_code}, update customer references]""")
        ])
    
    async def generate_test_case(self, requirement: TestCaseRequirement, 
                               user_story: str) -> Optional[TestCase]:
        """Generate test case with mandatory step preservation and LLM understanding summary"""
        
        print(f"    Generating test case with mandatory step preservation...")
        
        # Find best template
        template = await self._find_best_template_with_rag(requirement, user_story)
        
        if not template:
            print(f"     No suitable template found")
            return None
        
        original_step_count = len(template.steps)
        print(f"    Using template: {template.id} ({original_step_count} steps)")
        
        # Get contexts
        rag_context_text = self._get_rag_context_for_generation(requirement, user_story)
        
        # Extract requirement details with proper service code logic
        customer_status = getattr(requirement, 'customer_status', 'new' if requirement.scenario_type == 'install' else 'existing')
        eero_type = getattr(requirement, 'eero_type', 'eero')
        service_code = self._get_correct_service_code(requirement)
        
        print(f"    Target: {customer_status} {requirement.customer_type} {eero_type} ({service_code})")
        print(f"     MANDATE: Must preserve ALL {original_step_count} steps from template")
        
        try:
            # Use simplified chain for o1-mini compatibility
            chain = self.generation_prompt | self.llm
            
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'customer_status': customer_status,
                'scenario_type': requirement.scenario_type,
                'eero_type': eero_type,
                'service_code': service_code,
                'rag_context': rag_context_text,
                'template_content': template.content,
                'step_count': original_step_count,
                'user_story': user_story,
                'truck_roll_type': requirement.truck_roll_type
            })
            
            # Parse response manually for o1-mini
            generated_content = self._parse_o1_mini_response(response.content)
            
            if not generated_content or not generated_content.get('complete_steps'):
                print(f"    Generation produced empty or invalid content")
                print(f"    Raw response: {response.content[:200]}...")
                return None
            
            # Extract LLM understanding summary
            understanding_summary = self._extract_llm_understanding(generated_content.get('complete_steps', ''))
            print(f"    LLM Understanding: {understanding_summary}")
            
            # Parse and verify step preservation with enhanced validation
            generated_steps = self._parse_steps_comprehensive(generated_content.get('complete_steps', ''))
            generated_step_count = len(generated_steps)
            
            print(f"    Step verification: Template={original_step_count}, Generated={generated_step_count}")
            
            # Special handling for device removal scenarios
            combination_id = getattr(requirement, 'combination_id', None)
            if combination_id in [29, 30, 31]:
                print(f"    Special device removal scenario detected: ID {combination_id}")
                print(f"    Service code: {service_code} for {requirement.customer_type} customer")
            
            # Enhanced step preservation check with strict validation
            quality_check = self._validate_generated_quality(generated_steps, template, original_step_count)
            
            if not quality_check['valid']:
                print(f"    QUALITY CHECK FAILED: {quality_check['reason']}")
                print(f"    Expected={original_step_count}, Got={generated_step_count}")
                print(f"    Attempting aggressive step recovery...")
                
                # Force complete step recovery with strict validation
                recovered_content = await self._force_complete_step_recovery(
                    template, requirement, user_story, rag_context_text
                )
                
                if recovered_content:
                    # Re-validate recovered content
                    recovered_steps = self._parse_steps_comprehensive(recovered_content)
                    recovery_check = self._validate_generated_quality(recovered_steps, template, original_step_count)
                    
                    if recovery_check['valid']:
                        generated_content['complete_steps'] = recovered_content
                        generated_steps = recovered_steps
                        print(f"    Recovery successful: {len(generated_steps)}/{original_step_count} steps")
                    else:
                        print(f"    Recovery validation failed: {recovery_check['reason']}")
                        return None
                else:
                    print(f"    Recovery failed - REJECTING incomplete generation")
                    return None
            
            # Verify combination understanding
            combination_verification = self._verify_combination_understanding(generated_content.get('complete_steps', ''), requirement)
            print(f"    Combination verification: {combination_verification}")
            
            # Generate unique test case ID
            unique_id = self._generate_unique_id(
                generated_content.get('customer_type', requirement.customer_type), 
                generated_content.get('scenario_type', requirement.scenario_type), 
                service_code, 
                generated_content.get('testcase_id', 'generated')
            )
            
            # Create test case using parsed response
            new_test_case = TestCase(
                id=unique_id,
                title=generated_content.get('testcase_name', f'Generated {requirement.customer_type} {requirement.scenario_type} test case'),
                customer_type=generated_content.get('customer_type', requirement.customer_type),
                customer_status=generated_content.get('customer_status', customer_status),
                scenario_type=generated_content.get('scenario_type', requirement.scenario_type),
                truck_roll_type=generated_content.get('truck_roll_type', requirement.truck_roll_type),
                content=f"Testcase_id: {unique_id}\nTestcase_name: {generated_content.get('testcase_name', 'Generated Test Case')}\nTest_steps:\n{generated_content.get('complete_steps', '')}",
                steps=generated_steps,
                is_generated=True,
                template_sources=[template.id],
                generation_reasoning=f"Generated from template {template.id} preserving ALL {generated_content.get('step_count', original_step_count)} steps with {eero_type} adaptations and {service_code} service codes."
            )
            
            print(f"    Generated complete test case: {unique_id} ({len(generated_steps)}/{original_step_count} steps)")
            return new_test_case
            
        except Exception as e:
            print(f"    Generation failed: {e}")
            return None
    
    def _parse_o1_mini_response(self, response_text: str) -> dict:
        """Parse o1-mini response into structured format"""
        result = {}
        lines = response_text.split('\n')
        
        # Parse structured fields
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'testcase_id':
                    result['testcase_id'] = value
                elif key == 'testcase_name':
                    result['testcase_name'] = value
                elif key == 'customer_type':
                    result['customer_type'] = value
                elif key == 'customer_status':
                    result['customer_status'] = value
                elif key == 'scenario_type':
                    result['scenario_type'] = value
                elif key == 'truck_roll_type':
                    result['truck_roll_type'] = value
                elif key == 'step_count':
                    try:
                        result['step_count'] = int(value)
                    except:
                        result['step_count'] = 0
                elif key == 'complete_steps':
                    # Find the complete_steps content (everything after this line)
                    complete_steps_index = response_text.find('complete_steps:')
                    if complete_steps_index != -1:
                        steps_content = response_text[complete_steps_index + len('complete_steps:'):].strip()
                        result['complete_steps'] = steps_content
                    break
        
        # If complete_steps not found via the above method, try to extract test steps
        if 'complete_steps' not in result or not result['complete_steps']:
            # Look for test steps patterns
            test_steps_patterns = [
                r'Test_steps:\s*\n(.*)', 
                r'test_steps:\s*\n(.*)', 
                r'Steps:\s*\n(.*)',
                r'complete_steps:\s*\n(.*)',
                r'1\.\s*(.+)'  # Look for numbered steps
            ]
            
            for pattern in test_steps_patterns:
                match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if match:
                    result['complete_steps'] = match.group(1).strip()
                    break
            
            # Last resort - take everything after first numbered step
            if 'complete_steps' not in result or not result['complete_steps']:
                first_step_match = re.search(r'1\.\s*', response_text)
                if first_step_match:
                    result['complete_steps'] = response_text[first_step_match.start():].strip()
        
        return result
    
    def _validate_generated_quality(self, generated_steps: List[Dict[str, str]], 
                                   template: TestCase, expected_count: int) -> dict:
        """Validate the quality of generated test case against template standards"""
        
        if not generated_steps:
            return {'valid': False, 'reason': 'No steps generated'}
        
        step_count = len(generated_steps)
        
        # Check step count
        if step_count != expected_count:
            return {'valid': False, 'reason': f'Step count mismatch: expected {expected_count}, got {step_count}'}
        
        # Check step content quality
        empty_steps = [step for step in generated_steps if not step.get('action', '').strip()]
        if empty_steps:
            return {'valid': False, 'reason': f'{len(empty_steps)} steps have empty content'}
        
        # Check minimum content length per step (should be substantial)
        short_steps = [step for step in generated_steps if len(step.get('action', '')) < 10]
        if len(short_steps) > len(generated_steps) * 0.3:  # More than 30% are too short
            return {'valid': False, 'reason': f'{len(short_steps)} steps are too short (less than 10 characters)'}
        
        # Check that steps are numbered sequentially
        try:
            step_numbers = [int(step.get('step_number', 0)) for step in generated_steps]
            expected_numbers = list(range(1, step_count + 1))
            if step_numbers != expected_numbers:
                return {'valid': False, 'reason': f'Non-sequential step numbering: {step_numbers}'}
        except ValueError:
            return {'valid': False, 'reason': 'Invalid step numbering format'}
        
        # Check content similarity to template (basic check)
        template_content_lower = template.content.lower()
        generated_content = ' '.join([step.get('action', '') for step in generated_steps]).lower()
        
        # Should contain some key domain terms from the template
        domain_terms = ['acsr', 'customer', 'eero', 'order', 'service']
        matching_terms = [term for term in domain_terms if term in generated_content]
        
        if len(matching_terms) < 3:
            return {'valid': False, 'reason': f'Generated content lacks domain context (only {len(matching_terms)} domain terms found)'}
        
        return {'valid': True, 'reason': 'Quality validation passed'}
    
    async def _force_complete_step_recovery(self, template: TestCase, requirement: TestCaseRequirement, 
                                          user_story: str, rag_context: str) -> Optional[str]:
        """Force complete step recovery using aggressive template-based approach"""
        
        print(f"    Forcing complete step recovery...")
        
        # Create simplified recovery prompt
        recovery_prompt = ChatPromptTemplate.from_messages([
            ("system", """You generate complete test cases by copying ALL steps from templates.

**RULES:**
1. Copy exactly {step_count} steps from template
2. Change service codes: RESI uses HE***, BUSI uses BHSY*
3. Update customer type (RESI/BUSI) throughout
4. Keep all step details and expected results
5. Must generate {step_count} steps - no more, no less

**SERVICE CODES:**
- RESI: HE008, HE009, HE015
- BUSI Install: BHSY1, BHSY2, BHSY3
- BUSI CoS: BHSY5 (Eero W2W), BHSY6 (Eero Additional) - NO basic codes

**CRITICAL FOR BUSI CoS:**
Business Change of Service scenarios can ONLY use BHSY5 or BHSY6. Never use basic eero service codes for BUSI CoS."""),
            
            ("human", """**Template ({step_count} steps):** {template_content}

**Target:**
- Customer: {customer_type} ({customer_status})
- Service Code: {service_code}
- Scenario: {scenario_type}

**Task:** Copy all {step_count} steps, change service codes to {service_code}, update customer type.

Generate {step_count} steps now:""")
        ])
        
        try:
            customer_status = getattr(requirement, 'customer_status', 'existing')
            eero_type = getattr(requirement, 'eero_type', 'eero')
            service_code = self._get_correct_service_code(requirement)
            
            chain = recovery_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'customer_status': customer_status,
                'scenario_type': requirement.scenario_type,
                'eero_type': eero_type,
                'service_code': service_code,
                'template_content': template.content,
                'rag_context': rag_context,
                'step_count': len(template.steps),
                'user_story': user_story,
                'truck_roll_type': requirement.truck_roll_type
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"    Force recovery failed: {e}")
            return None
    
    def _extract_llm_understanding(self, generated_content: str) -> str:
        """Extract LLM understanding summary from generated content"""
        lines = generated_content.split('\n')
        understanding = []
        
        in_summary = False
        for line in lines:
            if 'understanding summary' in line.lower() or 'target customer' in line.lower():
                in_summary = True
                continue
            elif in_summary and line.strip():
                if any(marker in line for marker in ['##', '**', 'Step 1', 'Prerequisite']):
                    break
                understanding.append(line.strip())
        
        return '; '.join(understanding[:3]) if understanding else "No understanding summary found"
    
    def _verify_combination_understanding(self, content: str, requirement: TestCaseRequirement) -> dict:
        """Verify that LLM understood the combination correctly"""
        content_lower = content.lower()
        
        verification = {
            "service_code_applied": False,
            "customer_type_correct": False,
            "eero_type_understood": False,
            "scenario_appropriate": False
        }
        
        # Check service code application
        target_service_code = self._get_correct_service_code(requirement)
        verification["service_code_applied"] = target_service_code.lower() in content_lower
        
        # Check customer type
        if requirement.customer_type == 'RESI':
            verification["customer_type_correct"] = any(word in content_lower for word in ['residential', 'home'])
        else:
            verification["customer_type_correct"] = any(word in content_lower for word in ['business', 'commercial'])
        
        # Check eero type understanding
        eero_type = getattr(requirement, 'eero_type', 'eero')
        if 'plus' in eero_type:
            verification["eero_type_understood"] = any(word in content_lower for word in ['plus', 'premium', 'enhanced'])
        elif 'additional' in eero_type:
            verification["eero_type_understood"] = any(word in content_lower for word in ['additional', 'multiple', 'mesh'])
        else:
            verification["eero_type_understood"] = 'eero' in content_lower
        
        # Check scenario appropriateness
        verification["scenario_appropriate"] = requirement.scenario_type in content_lower
        
        return verification
    
    def _get_rag_context_for_generation(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get relevant RAG context for test case generation with device lifecycle intelligence"""
        if not self.rag_context:
            return "No specific business context available for generation."
        
        context_text = "## BUSINESS CONTEXT FOR GENERATION:\n\n"
        
        try:
            # Get combination intelligence from RAG
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            
            context_text += f"**Detected Business Pattern:** {combo_intel.get('detected_combination', 'standard_eero')}\n"
            context_text += f"**Workflow Type:** {combo_intel.get('workflow_type', 'standard_workflow')}\n"
            
            # Device lifecycle intelligence
            story_lower = user_story.lower()
            association_keywords = ["association", "associate", "binding", "bind", "device management", "account-to-device", "partner account"]
            if any(keyword in story_lower for keyword in association_keywords):
                context_text += f"**Device Lifecycle Context:** Association process requires comprehensive device management testing\n"
                context_text += f"**Removal Scenarios Required:** Generate test cases for device removal (gateway vs non-gateway scenarios)\n"
                context_text += f"**Business Priority:** Include business segment removal combinations (IDs 29-31) for complete coverage\n"
            
            # Get relevant business contexts
            story_keywords = [word.lower() for word in user_story.split() 
                            if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that']]
            
            relevant_contexts = []
            for keyword in story_keywords[:5]:
                contexts = self.rag_context.search_context(keyword)
                relevant_contexts.extend(contexts[:2])
            
            if relevant_contexts:
                context_text += f"\n**Business Validation Requirements:**\n"
                unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in relevant_contexts[:3]}
                
                for ctx in unique_contexts.values():
                    context_text += f"- Purpose: {ctx.get('business_purpose', 'Standard validation')}\n"
                    context_text += f"- Category: {ctx.get('test_category', 'General')}\n"
                    context_text += f"- Keywords: {', '.join(ctx.get('keywords', []))}\n"
            
            # Get customer segment specific context
            segment = 'residential' if requirement.customer_type == 'RESI' else 'business'
            segment_contexts = self.rag_context.get_context_by_customer_segment(segment)
            
            if segment_contexts:
                context_text += f"\n**{segment.title()} Segment Requirements:**\n"
                for ctx in segment_contexts[:2]:
                    context_text += f"- {ctx.get('business_purpose', 'Standard requirements')}\n"
            
        except Exception as e:
            context_text += f"Standard business validation required. (RAG error: {e})\n"
        
        return context_text
    
    def _get_combination_details(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get combination details using RAG context intelligence"""
        if not self.rag_context:
            return "## COMBINATION DETAILS:\n\nBasic eero combination with standard service codes."
        
        try:
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            
            details = f"## COMBINATION INTELLIGENCE:\n\n"
            details += f"**Detected Type:** {combo_intel.get('detected_combination', 'base_eero')}\n"
            details += f"**Workflow Pattern:** {combo_intel.get('workflow_type', 'standard_install')}\n"
            
            # Get product information
            product_info = combo_intel.get('product_info', {})
            if product_info:
                details += f"\n**Product Specifications:**\n"
                details += f"- Service Codes: {', '.join(product_info.get('service_codes', ['HE008']))}\n"
                details += f"- Features: {', '.join(product_info.get('features', ['basic_wifi']))}\n"
                details += f"- API Endpoints: {', '.join(product_info.get('api_endpoints', ['/eero/basic/']))}\n"
            
            # Get modification rules
            modification_rules = combo_intel.get('modification_rules', {})
            if modification_rules:
                details += f"\n**Required Adaptations:**\n"
                
                service_codes = modification_rules.get('service_codes', {})
                if service_codes:
                    details += f"- Service Code Changes: {service_codes}\n"
                
                validation_steps = modification_rules.get('validation_steps', [])
                if validation_steps:
                    details += f"- Additional Validations: {', '.join(validation_steps)}\n"
            
            # Get specific adaptations
            adaptations = combo_intel.get('specific_adaptations', [])
            if adaptations:
                details += f"\n**Specific Adaptations:**\n"
                for adaptation in adaptations:
                    details += f"- {adaptation}\n"
            
        except Exception as e:
            details = f"## COMBINATION DETAILS:\n\nStandard eero combination. (Intelligence error: {e})"
        
        return details
    
    def _generate_unique_id(self, customer_type: str, scenario_type: str, service_code: str, base_id: str) -> str:
        """Generate unique test case ID with collision detection"""
        # Create base ID components
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = str(uuid.uuid4())[:8]
        counter_suffix = f"{self._id_counter:03d}"
        
        # Build unique ID
        unique_id = f"TC_GEN_{customer_type}_{scenario_type}_{service_code}_{timestamp}_{counter_suffix}_{unique_suffix}"
        
        # Ensure uniqueness
        while unique_id in self._generated_ids:
            self._id_counter += 1
            counter_suffix = f"{self._id_counter:03d}"
            unique_suffix = str(uuid.uuid4())[:8]
            unique_id = f"TC_GEN_{customer_type}_{scenario_type}_{service_code}_{timestamp}_{counter_suffix}_{unique_suffix}"
        
        # Track generated ID
        self._generated_ids.add(unique_id)
        self._id_counter += 1
        
        return unique_id
    
    def _get_correct_service_code(self, requirement: TestCaseRequirement) -> str:
        """Get correct service code based on RESI/BUSI rules"""
        # RESI customers get HE*** codes, BUSI customers get BHSY* codes
        if requirement.customer_type == 'RESI':
            eero_type = getattr(requirement, 'eero_type', 'eero')
            if 'plus' in eero_type or 'premium' in eero_type:
                return 'HE009'  # Eero Plus
            elif 'secure' in eero_type:
                return 'HE015'  # Eero Secure Plus  
            else:
                return 'HE008'  # Basic Eero
        else:  # BUSI
            eero_type = getattr(requirement, 'eero_type', 'eero')
            combination_id = getattr(requirement, 'combination_id', None)
            
            # BUSI CoS scenarios - only BHSY5/BHSY6 allowed
            if requirement.scenario_type == 'cos':
                # Device removal scenarios (IDs 29-31)
                if combination_id in [29, 30, 31] or 'remove' in eero_type:
                    return 'BHSY5'  # Eero W2W for removal scenarios
                # Additional device scenarios
                elif 'additional' in eero_type:
                    return 'BHSY6'  # Eero Additional
                # Default CoS scenarios
                else:
                    return 'BHSY5'  # Eero W2W (default for BUSI CoS)
            
            # BUSI Install scenarios - use BHSY1-BHSY3
            else:
                if 'plus' in eero_type:
                    return 'BHSY2'  # Business Plus
                elif 'additional' in eero_type:
                    return 'BHSY3'  # Business Additional
                else:
                    return 'BHSY1'  # Basic business install
    
    def _verify_business_context_integration(self, content: str, rag_context: str) -> dict:
        """Verify that business context was properly integrated"""
        content_lower = content.lower()
        context_lower = rag_context.lower()
        
        verification = {
            "business_terms_included": False,
            "validation_patterns_applied": False,
            "context_keywords_present": False
        }
        
        # Check for business terms from context
        business_terms = ['validation', 'verification', 'business', 'purpose', 'requirements']
        verification["business_terms_included"] = any(term in content_lower for term in business_terms)
        
        # Check for validation patterns
        validation_patterns = ['kafka', 'api', 'insight', 'endpoint', 'response']
        verification["validation_patterns_applied"] = any(pattern in content_lower for pattern in validation_patterns)
        
        # Check for context-specific keywords
        if 'keywords:' in context_lower:
            context_keywords = context_lower.split('keywords:')[1].split('\n')[0].split(',')
            context_keywords = [kw.strip() for kw in context_keywords if kw.strip()]
            verification["context_keywords_present"] = any(kw in content_lower for kw in context_keywords[:3])
        
        return verification
    
    def _parse_steps_comprehensive(self, content: str) -> List[Dict[str, str]]:
        """Enhanced step parsing with comprehensive pattern matching identical to test_case_parser.py"""
        lines = content.split('\n')
        steps = []
        current_step = {}
        in_test_steps = False
        
        # Enhanced step patterns (same as test_case_parser.py)
        step_patterns = [
            r'^(\d+)\.\s*$',  # Step number alone on a line
            r'^(\d+)\.\s*(.+)',  # Step number with content
            r'^\s*(\d+)\s*\.\s*(.+)',  # Step with possible leading spaces
            r'^Step\s*(\d+):\s*(.+)',  # "Step 1: Description"
            r'^(\d+)\)\s*(.+)',  # "1) Step description"
            r'^\*\*Step\s*(\d+)\*\*:?\s*(.+)',  # "**Step 1**: Description"
            r'^\*\*(\d+)\.\s*(.+?)\*\*',  # "**1. Step description**"
            r'^##\s*Step\s*(\d+)[:.]?\s*(.*)',  # "## Step 1: Description"
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for Test_steps section or assume we're in it
            if 'Test_steps:' in line or 'test_steps:' in line.lower():
                in_test_steps = True
                i += 1
                continue
            
            # If we find step patterns, assume we're in test steps
            if not in_test_steps:
                for pattern in step_patterns:
                    if re.match(pattern, line):
                        in_test_steps = True
                        break
            
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
        
        # Final validation: ensure sequential step numbering
        if steps:
            # Sort by step number
            try:
                steps.sort(key=lambda x: int(x['step_number']))
                
                # Log step count for debugging
                print(f"    Parsed {len(steps)} steps successfully")
                for step in steps[:3]:  # Show first 3 steps for verification
                    print(f"      Step {step['step_number']}: {step['action'][:50]}...")
                    
            except ValueError as e:
                print(f"    Warning: Step numbering issue: {e}")
        
        return steps
    
    async def _find_best_template_with_rag(self, requirement: TestCaseRequirement, user_story: str) -> Optional[TestCase]:
        """Find best template using RAG context and combination intelligence with template diversity"""
        
        if not self.rag_context:
            return self._find_best_template_basic(requirement)
        
        try:
            # Get combination intelligence for better template selection
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            combination_type = combo_intel.get('detected_combination', 'base_eero')
            
            print(f"    Using RAG intelligence: {combination_type}")
            
            # Score templates with RAG intelligence and diversity bonus
            scored_templates = []
            
            for tc in self.test_cases:
                if tc.is_generated:
                    continue
                
                score = 0
                
                # Basic matching (40 points)
                if tc.customer_type == requirement.customer_type:
                    score += 15
                if tc.scenario_type == requirement.scenario_type:
                    score += 20
                if tc.truck_roll_type == requirement.truck_roll_type:
                    score += 5
                
                # RAG-based combination relevance (40 points)
                tc_content_lower = tc.content.lower()
                if combination_type == "eero_plus" and any(word in tc_content_lower for word in ["plus", "premium", "secure"]):
                    score += 40
                elif combination_type == "multiple_devices" and any(word in tc_content_lower for word in ["multiple", "additional", "mesh"]):
                    score += 40
                elif combination_type == "base_eero" and not any(word in tc_content_lower for word in ["plus", "premium", "multiple"]):
                    score += 30
                elif "eero" in tc_content_lower:
                    score += 20
                
                # Quality and completeness (20 points)
                if len(tc.steps) > 8:
                    score += 10
                if len(tc.content) > 3000:
                    score += 10
                
                # Template diversity bonus - penalize recently used templates (up to -30 points)
                if tc.id in self._used_templates:
                    penalty = min(30, len(self._used_templates) * 5)
                    score -= penalty
                    print(f"    Template {tc.id} penalty: -{penalty} (recently used)")
                
                # Service code variety bonus
                service_code = self._get_correct_service_code(requirement)
                if service_code in tc.content:
                    score += 5  # Small bonus for matching service code
                
                scored_templates.append((score, tc))
            
            if not scored_templates:
                return None
            
            # Sort by score and get top candidates
            scored_templates.sort(key=lambda x: x[0], reverse=True)
            
            # Select best unused template if available, otherwise best overall
            best_template = None
            for score, template in scored_templates:
                if template.id not in self._used_templates:
                    best_template = template
                    best_score = score
                    break
            
            # If all templates have been used recently, use the best scoring one
            if not best_template:
                best_score, best_template = scored_templates[0]
                # Clear used templates if all have been used
                if len(self._used_templates) >= len([tc for tc in self.test_cases if not tc.is_generated]):
                    self._used_templates.clear()
                    print(f"    Cleared template usage history for diversity")
            
            # Track template usage
            self._used_templates.add(best_template.id)
            
            # Limit tracking to last 5 templates
            if len(self._used_templates) > 5:
                oldest_template = next(iter(self._used_templates))
                self._used_templates.remove(oldest_template)
            
            print(f"    Best template: {best_template.id} (RAG score: {best_score}/100)")
            print(f"    Used templates: {list(self._used_templates)}")
            return best_template
            
        except Exception as e:
            print(f"     RAG template selection failed: {e}, using basic selection")
            return self._find_best_template_basic(requirement)
    
    def _find_best_template_basic(self, requirement: TestCaseRequirement) -> Optional[TestCase]:
        """Basic template selection fallback with diversity consideration"""
        matching_templates = [
            tc for tc in self.test_cases
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated)
        ]
        
        if not matching_templates:
            return None
        
        # Prefer unused templates for diversity
        unused_templates = [tc for tc in matching_templates if tc.id not in self._used_templates]
        
        if unused_templates:
            # Return unused template with most steps (highest quality)
            best_template = max(unused_templates, key=lambda tc: len(tc.steps))
        else:
            # If all templates have been used, return template with most steps
            best_template = max(matching_templates, key=lambda tc: len(tc.steps))
            # Clear usage history if all templates have been used
            if len(self._used_templates) >= len(matching_templates):
                self._used_templates.clear()
                print(f"    Cleared template usage history (basic fallback)")
        
        # Track template usage
        if best_template:
            self._used_templates.add(best_template.id)
            # Limit tracking to last 5 templates
            if len(self._used_templates) > 5:
                oldest_template = next(iter(self._used_templates))
                self._used_templates.remove(oldest_template)
        
        return best_template

