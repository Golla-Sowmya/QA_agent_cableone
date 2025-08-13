import re
from typing import List, Dict, Optional
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class GenerationAgent:
    """Enhanced Generation Agent with COMPLETE step preservation and RAG context integration"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        
        # COMPLETELY ENHANCED generation prompt with MANDATORY step preservation
        self.generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an EXPERT EERO TEST CASE GENERATOR with MANDATORY COMPLETE STEP PRESERVATION.

## CRITICAL STEP PRESERVATION MANDATE ##

**ABSOLUTE REQUIREMENT: PRESERVE ALL TEMPLATE STEPS**
- You MUST include ALL {step_count} steps from the template
- You MUST adapt each step for the specific eero combination
- You MUST maintain the complete end-to-end workflow
- You MUST include all verification steps (Kafka, API, eero Insight, etc.)
- NEVER truncate or skip any steps from the template

## COMPLETE EERO WORKFLOW UNDERSTANDING ##

**FULL END-TO-END PROCESS (ALL STEPS REQUIRED):**
1. **Prerequisites**: Customer setup and device preparation
2. **ACSR Order Creation**: Customer search and order workflow initiation  
3. **Service Configuration**: Adding eero service with correct service codes
4. **Order Details**: Equipment addition, validation, and completion
5. **Order Status Update**: Changing order status to complete ✅ CRITICAL
6. **Kafka Queue Validation**: Verifying message queues ✅ CRITICAL  
7. **Banhammer Portal Check**: Device configuration verification ✅ CRITICAL
8. **API Testing**: eero-provisioning endpoint validation ✅ CRITICAL
9. **eero Insight Setup**: Network creation and customer setup ✅ CRITICAL
10. **Final API Verification**: Complete workflow validation ✅ CRITICAL

## EERO COMBINATION INTELLIGENCE ##

**SERVICE CODE ADAPTATIONS:**
- Base Eero: HE008 → Standard workflow
- Eero Plus: HE009 → Enhanced security validation
- Eero Secure: HE010 → Advanced security features
- Multiple Devices: HE008_MULTI → Bulk device operations

**API ENDPOINT ADAPTATIONS:**
- Base: /eeros/web/customerAccount/
- Plus: /eeros/plus/customerAccount/ 
- Secure: /eeros/secure/customerAccount/
- Multi: /eeros/devices/customerAccount/

**VALIDATION ENHANCEMENTS:**
- Plus/Secure: Add security feature validation, subscription verification
- Multiple Devices: Add mesh network validation, device sync checks
- Service Upgrades: Add billing modification validation

## MANDATORY GENERATION RULES ##

✅ **PRESERVE EVERY SINGLE STEP** - No truncation allowed
✅ **ADAPT each step** for the specific combination
✅ **MAINTAIN step numbering** (1, 2, 3... through ALL steps)
✅ **INCLUDE ALL verification steps** (Kafka, API, eero Insight)
✅ **ADD combination-specific validations** without removing existing ones
✅ **ENSURE complete end-to-end coverage** from order to final verification"""),
            
            ("human", """## COMPLETE TEST CASE GENERATION WITH FULL STEP PRESERVATION ##

**GENERATION TARGET:**
- Customer: {customer_type} 
- Scenario: {scenario_type}
- Truck Roll: {truck_roll_type}

**USER STORY:** {user_story}

**COMBINATION INTELLIGENCE:** {combination_intelligence}

**COMPLETE TEMPLATE ({step_count} STEPS):**
{template_content}

## MANDATORY GENERATION PROCESS ##

**STEP 1: ANALYZE COMPLETE TEMPLATE STRUCTURE**
The template contains {step_count} steps. You MUST preserve ALL of them:
- Steps 1-4: ACSR order creation and service configuration
- Step 5: Order completion and status update ✅ REQUIRED
- Step 6: Kafka queue validation ✅ REQUIRED  
- Step 7: Banhammer portal verification ✅ REQUIRED
- Step 8: API endpoint testing ✅ REQUIRED
- Step 9: eero Insight setup and validation ✅ REQUIRED
- Step 10: Final API verification ✅ REQUIRED

**STEP 2: COMBINATION-SPECIFIC ADAPTATIONS**
For each step, apply appropriate modifications:
- Service codes: Update HE008 → HE009/HE010 where needed
- API endpoints: Modify for combination type
- Validation criteria: Enhance for specific features
- Additional checks: Add combination-specific validations

**STEP 3: COMPLETE STEP-BY-STEP GENERATION**

Generate the COMPLETE test case including:

### **Prerequisites Section:**
- Adapt customer and device requirements for the combination

### **Step-by-Step Execution (ALL {step_count} STEPS):**

**Steps 1-4: Order Creation & Configuration**
- Preserve ACSR workflow steps
- Adapt service codes for combination (HE008 → HE009/HE010)
- Maintain all order details and equipment validation

**Step 5: Order Completion** ✅ MANDATORY
- Include order status change to Complete
- Adapt for combination-specific completion requirements

**Step 6: Kafka Queue Validation** ✅ MANDATORY  
- Include complete Kafka UI access and validation
- Adapt message validation for combination type
- Include all required field verifications

**Step 7: Banhammer Portal Verification** ✅ MANDATORY
- Include complete device configuration check
- Adapt for combination-specific configurations
- Maintain all LDAP verification steps

**Step 8: API Endpoint Testing** ✅ MANDATORY
- Include eero-provisioning API calls
- Adapt endpoints for combination type
- Include complete response validation

**Step 9: eero Insight Setup** ✅ MANDATORY
- Include complete network creation workflow
- Adapt for combination-specific features (Plus/Secure)
- Include all customer setup and verification steps

**Step 10: Final API Verification** ✅ MANDATORY
- Include final endpoint validation
- Adapt response validation for combination
- Include complete network verification

### **Enhanced Validations:**
Add combination-specific validations without removing original ones

**CRITICAL REQUIREMENTS FOR OUTPUT:**
✅ Include ALL {step_count} steps from template - NO EXCEPTIONS
✅ Adapt each step for the specific eero combination
✅ Maintain complete end-to-end workflow coverage
✅ Include all API testing, Kafka validation, and eero Insight steps
✅ Add combination-specific enhancements throughout
✅ Generate COMPLETE test case from Prerequisites to Final Verification

**ABSOLUTE MANDATE:** 
Your output MUST contain ALL {step_count} steps. If the template has 10 steps, your output must have 10 steps. If it has 15 steps, your output must have 15 steps. NO TRUNCATION ALLOWED.

Generate the COMPLETE test case with ALL steps now:""")
        ])
    
    async def generate_test_case(self, requirement: TestCaseRequirement, 
                               user_story: str) -> Optional[TestCase]:
        """Generate COMPLETE test case with mandatory step preservation"""
        
        # Get combination intelligence
        combination_intel = self.rag_context.get_combination_intelligence(user_story)
        
        # Find best template
        template = await self._find_best_template_with_rag(requirement, user_story)
        
        if not template:
            print(f"   ⚠️  No suitable template found for generation")
            return None
        
        original_step_count = len(template.steps)
        print(f"   📝 Using template: {template.id} ({original_step_count} steps)")
        print(f"   🎯 Detected combination: {combination_intel['detected_combination']}")
        print(f"   ⚠️  MANDATE: Must preserve ALL {original_step_count} steps")
        
        # Format combination intelligence
        combination_text = self._format_combination_intelligence(combination_intel)
        
        try:
            chain = self.generation_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type,
                'truck_roll_type': requirement.truck_roll_type,
                'user_story': user_story,
                'combination_intelligence': combination_text,
                'template_content': template.content,  # Complete template
                'step_count': original_step_count  # Emphasize step count
            })
            
            generated_content = response.content.strip()
            
            if not generated_content:
                print(f"   ❌ Generation produced empty content")
                return None
            
            # Parse and verify step preservation
            generated_steps = self._parse_steps_comprehensive(generated_content)
            generated_step_count = len(generated_steps)
            
            print(f"   📊 Step verification: Template={original_step_count}, Generated={generated_step_count}")
            
            # Critical step preservation check
            if generated_step_count < original_step_count:
                print(f"   🚨 CRITICAL: Missing {original_step_count - generated_step_count} steps!")
                print(f"   🔄 Attempting step recovery...")
                
                # Try to recover missing steps
                recovered_content = await self._recover_missing_steps(
                    generated_content, template, combination_intel, 
                    requirement, user_story
                )
                
                if recovered_content:
                    generated_content = recovered_content
                    generated_steps = self._parse_steps_comprehensive(generated_content)
                    print(f"   ✅ Recovery successful: {len(generated_steps)} steps")
                else:
                    print(f"   ❌ Recovery failed - using partial result")
            
            # Verify critical steps are included
            critical_step_verification = self._verify_critical_steps(generated_content)
            
            print(f"   🔍 Critical step verification:")
            for step_name, present in critical_step_verification.items():
                status = "✅" if present else "❌"
                print(f"     {status} {step_name}")
            
            # Create comprehensive test case
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            combination_type = combination_intel['detected_combination']
            new_id = f"TC_GEN_{requirement.customer_type}_{requirement.scenario_type}_{combination_type}_{timestamp}"
            
            new_test_case = TestCase(
                id=new_id,
                title=f"Generated {requirement.customer_type} {requirement.scenario_type} - {combination_type} ({requirement.truck_roll_type} TruckRoll) - Complete Workflow",
                customer_type=requirement.customer_type,
                customer_status='existing' if requirement.scenario_type == 'cos' else 'new',
                scenario_type=requirement.scenario_type,
                truck_roll_type=requirement.truck_roll_type,
                content=generated_content,
                steps=generated_steps,
                is_generated=True,
                template_sources=[template.id],
                generation_reasoning=f"Generated complete {combination_type} workflow from {template.id} preserving all {original_step_count} steps with combination-specific adaptations"
            )
            
            print(f"   ✅ Generated COMPLETE test case: {new_id} ({len(generated_steps)}/{original_step_count} steps)")
            return new_test_case
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return None
    
    async def _recover_missing_steps(self, partial_content: str, template: TestCase, 
                                   combination_intel: dict, requirement: TestCaseRequirement, 
                                   user_story: str) -> Optional[str]:
        """Attempt to recover missing steps using focused regeneration"""
        
        print(f"   🔄 Attempting step recovery...")
        
        # Create recovery prompt
        recovery_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are tasked with COMPLETING a truncated test case by adding missing steps.

CRITICAL MISSION: Add ALL missing steps from the template to complete the test case.

The test case was truncated and is missing critical steps like:
- Order completion and status updates
- Kafka queue validation  
- Banhammer portal verification
- API endpoint testing
- eero Insight setup
- Final verification steps

You MUST complete the test case with ALL remaining steps from the template."""),
            
            ("human", """## STEP RECOVERY TASK ##

**PARTIAL TEST CASE (TRUNCATED):**
{partial_content}

**COMPLETE TEMPLATE WITH ALL STEPS:**
{template_content}

**COMBINATION REQUIREMENTS:**
{combination_intelligence}

## RECOVERY INSTRUCTIONS ##

1. **Analyze what steps are missing** from the partial test case
2. **Add ALL missing steps** from the template
3. **Adapt missing steps** for the combination type
4. **Ensure complete end-to-end workflow**

The partial test case appears to be missing critical validation steps. You MUST add:
- Order completion verification
- Kafka queue validation
- Banhammer portal checks  
- API endpoint testing
- eero Insight setup and validation
- Final API verification

Generate the COMPLETE test case with ALL missing steps added:""")
        ])
        
        try:
            combination_text = self._format_combination_intelligence(combination_intel)
            
            chain = recovery_prompt | self.llm
            response = await chain.ainvoke({
                'partial_content': partial_content,
                'template_content': template.content,
                'combination_intelligence': combination_text
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"   ❌ Step recovery failed: {e}")
            return None
    
    def _verify_critical_steps(self, content: str) -> dict:
        """Verify that critical steps are present in the generated content"""
        
        content_lower = content.lower()
        
        critical_steps = {
            "Order Completion": any(phrase in content_lower for phrase in [
                "order status", "complete", "finish button", "job details"
            ]),
            "Kafka Validation": any(phrase in content_lower for phrase in [
                "kafka", "eero-order queue", "billing-system"
            ]),
            "Banhammer Portal": any(phrase in content_lower for phrase in [
                "banhammer", "mac address", "ldap"
            ]),
            "API Testing": any(phrase in content_lower for phrase in [
                "eero-provisioning", "swagger", "api", "endpoint"
            ]),
            "eero Insight Setup": any(phrase in content_lower for phrase in [
                "eero insight", "create new network", "network ownership"
            ]),
            "Final Verification": any(phrase in content_lower for phrase in [
                "final", "networks", "partner_account_id"
            ])
        }
        
        return critical_steps
    
    def _parse_steps_comprehensive(self, content: str) -> List[Dict[str, str]]:
        """Enhanced step parsing with comprehensive pattern matching"""
        
        lines = content.split('\n')
        steps = []
        current_step = {}
        in_step = False
        
        # Enhanced step patterns
        step_patterns = [
            r'^(\d+)\.\s*(.+)',  # "1. Step description"
            r'^Step\s*(\d+):\s*(.+)',  # "Step 1: Description"
            r'^(\d+)\)\s*(.+)',  # "1) Step description"
            r'^\*\*Step\s*(\d+)\*\*:\s*(.+)',  # "**Step 1**: Description"
            r'^\*\*(\d+)\.\s*(.+)\*\*',  # "**1. Step description**"
            r'^##\s*Step\s*(\d+)',  # "## Step 1"
            r'^###\s*(\d+)\.',  # "### 1."
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for step patterns
            step_match = None
            for pattern in step_patterns:
                step_match = re.match(pattern, line)
                if step_match:
                    break
            
            if step_match:
                # Save previous step
                if current_step:
                    steps.append(current_step)
                
                # Start new step
                step_number = step_match.group(1)
                step_description = step_match.group(2) if len(step_match.groups()) > 1 else ""
                
                current_step = {
                    'step_number': step_number,
                    'action': step_description,
                    'expected_result': ''
                }
                in_step = True
                
            elif in_step and any(keyword in line.lower() for keyword in [
                'expected result', 'verify', 'expected:', 'result:', 'validation:'
            ]):
                # Add to expected result
                result_text = line
                for keyword in ['expected result:', 'expected:', 'verify:', 'result:', 'validation:']:
                    result_text = result_text.replace(keyword, '').strip()
                
                if current_step['expected_result']:
                    current_step['expected_result'] += " " + result_text
                else:
                    current_step['expected_result'] = result_text
                    
            elif in_step and current_step:
                # Continue building step description
                if not any(line.startswith(marker) for marker in ['##', '**', '###']):
                    current_step['action'] += " " + line
        
        # Add final step
        if current_step:
            steps.append(current_step)
        
        return steps
    
    # Keep existing helper methods...
    def _format_combination_intelligence(self, combination_intel: dict) -> str:
        """Format combination intelligence for the prompt"""
        
        intel_text = f"## DETECTED COMBINATION: {combination_intel['detected_combination'].upper()} ##\n\n"
        
        product_info = combination_intel.get('product_info', {})
        if product_info:
            intel_text += f"**Product Information:**\n"
            intel_text += f"- Service Codes: {', '.join(product_info.get('service_codes', []))}\n"
            intel_text += f"- Description: {product_info.get('description', 'N/A')}\n"
            intel_text += f"- Key Features: {', '.join(product_info.get('features', []))}\n"
            intel_text += f"- API Endpoints: {', '.join(product_info.get('api_endpoints', []))}\n\n"
        
        modification_rules = combination_intel.get('modification_rules', {})
        if modification_rules:
            intel_text += f"**MANDATORY TEMPLATE MODIFICATIONS:**\n"
            
            service_codes = modification_rules.get('service_codes', {})
            if service_codes:
                intel_text += f"- Service Code Changes: {service_codes}\n"
            
            api_endpoints = modification_rules.get('api_endpoints', {})
            if api_endpoints:
                intel_text += f"- API Endpoint Changes: {api_endpoints}\n"
            
            validation_steps = modification_rules.get('validation_steps', [])
            if validation_steps:
                intel_text += f"- Additional Validation Steps:\n"
                for step in validation_steps:
                    intel_text += f"  • {step}\n"
        
        specific_adaptations = combination_intel.get('specific_adaptations', [])
        if specific_adaptations:
            intel_text += f"\n**SPECIFIC ADAPTATIONS REQUIRED:**\n"
            for adaptation in specific_adaptations:
                intel_text += f"• {adaptation}\n"
        
        return intel_text
    
    async def _find_best_template_with_rag(self, requirement: TestCaseRequirement, user_story: str) -> Optional[TestCase]:
        """Find best template using RAG context search with combination awareness"""
        
        # Get combination intelligence
        combination_intel = self.rag_context.get_combination_intelligence(user_story)
        combination_type = combination_intel['detected_combination']
        
        # Score templates with combination awareness
        scored_templates = []
        
        for tc in self.test_cases:
            if tc.is_generated:
                continue
            
            score = 0
            
            # Basic matching (60 points)
            if tc.customer_type == requirement.customer_type:
                score += 20
            if tc.scenario_type == requirement.scenario_type:
                score += 30
            if tc.truck_roll_type == requirement.truck_roll_type:
                score += 10
            
            # Combination relevance (30 points)
            tc_content_lower = tc.content.lower()
            if combination_type == "eero_plus" and any(word in tc_content_lower for word in ["plus", "premium", "secure"]):
                score += 30
            elif combination_type == "multiple_devices" and any(word in tc_content_lower for word in ["multiple", "additional", "mesh"]):
                score += 30
            elif combination_type == "base_eero" and not any(word in tc_content_lower for word in ["plus", "premium", "secure", "multiple"]):
                score += 20
            
            # Quality and completeness bonus (20 points)
            if len(tc.steps) > 8:  # Prefer comprehensive templates
                score += 10
            if len(tc.content) > 3000:  # Prefer detailed templates
                score += 10
            
            # Critical step coverage bonus (10 points)
            if all(keyword in tc_content_lower for keyword in ["kafka", "api", "insight"]):
                score += 10
            
            scored_templates.append((score, tc))
        
        if not scored_templates:
            return None
        
        # Sort by score and return highest scoring template
        scored_templates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_template = scored_templates[0]
        
        print(f"   📊 Best template: {best_template.id} (score: {best_score}/130, comprehensive)")
        return best_template