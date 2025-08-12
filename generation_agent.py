import re
from typing import List, Dict, Optional
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class GenerationAgent:
    """Enhanced Generation Agent with step preservation and RAG context integration"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context  # Add RAG context
        
        # Enhanced generation prompt with step preservation emphasis
# ONLY replace the generation_prompt in generation_agent.py

# ONLY replace the generation_prompt in generation_agent.py

        self.generation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Eero Product Combination Test Case Generator.

EERO PRODUCT COMBINATION EXPERTISE:
**Install Combinations:**
- Base Eero Install: Standard HE008 service setup
- Eero Plus/Secure Install: Enhanced service with security features (different service codes)
- Multiple Device Install: Installing additional eero devices in single workflow
- Enhanced Subscription Install: Premium eero services with advanced features

**Change of Service Combinations:**
- Add Plus/Secure: Upgrading existing eero to premium subscription
- Add Additional Devices: Adding more eero devices to existing setup
- Remove Devices: Removing specific eero devices from account
- Service Upgrade: Changing eero subscription levels

INTELLIGENT PRODUCT ADAPTATION:
- Analyze user story to identify SPECIFIC eero product combination needed
- Adapt template service codes, product names, and configurations for the specific combination
- Modify API endpoints, validation steps, and verification criteria for the product variant
- Ensure test case reflects the SPECIFIC eero product scenario, not just basic install/cos

COMBINATION-SPECIFIC ADAPTATION RULES:
- Base Eero: Use standard service codes and basic verification
- Plus/Secure: Adapt for enhanced service codes, security features, and premium verification
- Additional Devices: Modify for multiple device association and management workflows
- Service Upgrades: Adapt for subscription change workflows and billing modifications"""),
    
    ("human", """EERO PRODUCT COMBINATION GENERATION:

Generate test case for: {customer_type} {scenario_type} - {truck_roll_type} TruckRoll

User Story Context: {user_story}
RAG Context: {rag_context}

TEMPLATE REFERENCE:
{template_content}

PRODUCT COMBINATION ANALYSIS:
Analyze the user story to determine the SPECIFIC EERO PRODUCT COMBINATION needed:

1. **Combination Detection**: What specific eero product/service combination is required?
   - Is this base eero installation/service?
   - Is this eero plus/secure premium service?
   - Is this additional device management?
   - Is this service upgrade/downgrade?

2. **Adaptation Strategy**: How should the template be modified for this specific combination?
   - What service codes need to change? (HE008 vs premium codes)
   - What product names need adaptation? (Eero Wifi vs Eero Secure Plus)
   - What verification steps need modification for this product variant?
   - What API endpoints are specific to this eero combination?

INTELLIGENT ADAPTATION REQUIREMENTS:
✓ Preserve ALL steps from template while adapting for specific eero product combination
✓ Modify service codes, product names, and configurations for the detected combination
✓ Adapt verification and validation steps for the specific eero variant
✓ Ensure test case reflects the SPECIFIC eero product scenario from user story
✓ Create a DISTINCT test case that's different from basic eero scenarios

Generate the complete adapted test case for the specific eero product combination:""")
])
    
    async def generate_test_case(self, requirement: TestCaseRequirement, 
                               user_story: str) -> Optional[TestCase]:
        """Generate comprehensive test case preserving all steps"""
        
        # Find best template using RAG context
        template = await self._find_best_template_with_rag(requirement, user_story)
        
        if not template:
            print(f"   ⚠️  No suitable template found for generation")
            return None
        
        print(f"   📝 Using template: {template.id} ({len(template.steps)} steps)")
        
        # Get RAG context for this generation
        rag_context = self._get_rag_context_for_generation(requirement, user_story)
        
        # Generate explanations
        customer_explanation = self._get_customer_explanation(requirement.customer_type)
        scenario_explanation = self._get_scenario_explanation(requirement.scenario_type)
        truck_explanation = self._get_truck_roll_explanation(requirement.truck_roll_type)
        
        try:
            chain = self.generation_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type,
                'truck_roll_type': requirement.truck_roll_type,
                'customer_explanation': customer_explanation,
                'scenario_explanation': scenario_explanation,
                'truck_explanation': truck_explanation,
                'user_story': user_story,
                'rag_context': rag_context,
                'template_content': template.content,  # NO TRUNCATION - use full content
                'step_count': len(template.steps)  # Pass step count for emphasis
            })
            
            generated_content = response.content.strip()
            
            if not generated_content:
                print(f"   ❌ Generation produced empty content")
                return None
            
            # Verify step count
            generated_steps = self._parse_steps(generated_content)
            original_step_count = len(template.steps)
            generated_step_count = len(generated_steps)
            
            print(f"   📊 Step verification: Template={original_step_count}, Generated={generated_step_count}")
            
            if generated_step_count < (original_step_count * 0.8):  # If less than 80% of steps
                print(f"   ⚠️  Warning: Generated test case has significantly fewer steps")
            
            # Create new test case
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_id = f"TC_GEN_{requirement.customer_type}_{requirement.scenario_type}_{requirement.truck_roll_type}_{timestamp}"
            
            new_test_case = TestCase(
                id=new_id,
                title=f"Generated {requirement.customer_type} {requirement.scenario_type} - {requirement.truck_roll_type} TruckRoll",
                customer_type=requirement.customer_type,
                customer_status='existing' if requirement.scenario_type == 'cos' else 'new',
                scenario_type=requirement.scenario_type,
                truck_roll_type=requirement.truck_roll_type,
                content=generated_content,
                steps=generated_steps,
                is_generated=True,
                template_sources=[template.id],
                generation_reasoning=f"Generated from template {template.id} ({original_step_count} steps) using RAG context for {requirement.customer_type} {requirement.scenario_type} scenario"
            )
            
            print(f"   ✅ Generated comprehensive test case: {new_id} ({len(generated_steps)} steps)")
            return new_test_case
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return None
    
    async def _find_best_template_with_rag(self, requirement: TestCaseRequirement, user_story: str) -> Optional[TestCase]:
        """Find best template using RAG context search"""
        
        # Create search terms from requirement and user story
        search_terms = [
            requirement.customer_type.lower(),
            requirement.scenario_type.lower(),
            requirement.truck_roll_type.lower(),
            "eero", "association", "device"
        ]
        
        # Add terms from user story
        story_terms = [word.lower() for word in user_story.split() 
                      if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that']]
        search_terms.extend(story_terms[:5])  # Add top 5 story terms
        
        # Search RAG context for relevant test cases
        relevant_contexts = []
        for term in search_terms:
            try:
                contexts = self.rag_context.search_context(term)
                relevant_contexts.extend(contexts)
            except:
                continue
        
        # Get unique relevant test case names
        relevant_filenames = set()
        for context in relevant_contexts:
            filename = context.get('file_name', '')
            if filename:
                relevant_filenames.add(filename.replace('.txt', ''))
        
        print(f"   🔍 RAG found {len(relevant_filenames)} relevant test cases")
        
        # Score templates by RAG relevance + similarity
        scored_templates = []
        
        for tc in self.test_cases:
            if tc.is_generated:
                continue
            
            score = 0
            
            # RAG relevance bonus (40 points)
            tc_filename = tc.id.replace('TC_', '')
            if any(tc_filename in filename or filename in tc_filename for filename in relevant_filenames):
                score += 40
                print(f"   🎯 RAG match: {tc.id}")
            
            # Customer type match (20 points)
            if tc.customer_type == requirement.customer_type:
                score += 20
            
            # Scenario type match (30 points)
            if tc.scenario_type == requirement.scenario_type:
                score += 30
            
            # Truck roll match (10 points)  
            if tc.truck_roll_type == requirement.truck_roll_type:
                score += 10
            
            # Quality bonus (step count and content length)
            if len(tc.steps) > 10:
                score += 5
            if len(tc.content) > 2000:
                score += 5
            
            scored_templates.append((score, tc))
        
        if not scored_templates:
            return None
        
        # Sort by score and return highest scoring template
        scored_templates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_template = scored_templates[0]
        
        print(f"   📊 Best template: {best_template.id} (score: {best_score}/110)")
        return best_template
    
    def _get_rag_context_for_generation(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get comprehensive RAG context for generation"""
        
        # Search by customer segment
        segment_contexts = self.rag_context.get_context_by_customer_segment(
            'residential' if requirement.customer_type == 'RESI' else 'business'
        )
        
        # Search by category
        category = 'install' if requirement.scenario_type == 'install' else 'change_of_service'
        category_contexts = self.rag_context.get_context_by_category(category)
        
        # Combine and format context
        all_contexts = segment_contexts + category_contexts
        
        if not all_contexts:
            return "Apply standard telecommunications testing practices."
        
        # Remove duplicates
        unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in all_contexts}
        
        context_text = "## RELEVANT RAG BUSINESS CONTEXT:\n"
        for i, (filename, ctx) in enumerate(list(unique_contexts.items())[:3], 1):
            context_text += f"**Context {i}**: {ctx.get('context_summary', 'N/A')}\n"
            context_text += f"**Business Purpose**: {ctx.get('business_purpose', 'N/A')}\n"
            context_text += f"**Key Areas**: {', '.join(ctx.get('keywords', []))}\n"
            context_text += f"**Test Category**: {ctx.get('test_category', 'N/A')}\n\n"
        
        return context_text
    
    def _get_customer_explanation(self, customer_type: str) -> str:
        """Get customer type explanation"""
        if customer_type == "RESI":
            return "residential customer - individual/home user"
        else:
            return "business customer - commercial/enterprise client"
    
    def _get_scenario_explanation(self, scenario_type: str) -> str:
        """Get scenario explanation"""
        if scenario_type == "install":
            return "new customer installation - first time setup"
        else:
            return "change of service - existing customer modification"
    
    def _get_truck_roll_explanation(self, truck_roll_type: str) -> str:
        """Get truck roll explanation"""
        if truck_roll_type == "No":
            return "no technician visit required - customer self-installation"
        else:
            return "technician visit required for installation/setup"
    
    def _parse_steps(self, content: str) -> List[Dict[str, str]]:
        """Enhanced step parsing"""
        lines = content.split('\n')
        steps = []
        current_step = {}
        
        # Multiple step patterns to catch different formats
        step_patterns = [
            r'^(\d+)\.\s*(.+)',  # "1. Step description"
            r'^Step\s*(\d+):\s*(.+)',  # "Step 1: Description"
            r'^(\d+)\)\s*(.+)',  # "1) Step description"
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check all step patterns
            step_match = None
            for pattern in step_patterns:
                step_match = re.match(pattern, line)
                if step_match:
                    break
            
            if step_match:
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    'step_number': step_match.group(1),
                    'action': step_match.group(2),
                    'expected_result': ''
                }
            elif 'expected result' in line.lower() and current_step:
                result = line.replace('Expected result', '').replace('Expected Result', '').replace(':', '').strip()
                current_step['expected_result'] = result
        
        if current_step:
            steps.append(current_step)
        
        return steps