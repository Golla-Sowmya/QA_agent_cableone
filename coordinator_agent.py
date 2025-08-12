from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCaseRequirement

class CoordinatorAgent:
    """Enhanced Coordinator Agent with RAG context awareness"""
    
    def __init__(self, llm: AzureChatOpenAI, rag_context=None):  # Add rag_context parameter
        self.llm = llm
        self.rag_context = rag_context  # Store RAG context
        
        # Enhanced coordination prompt with RAG awareness
# ONLY replace the coordination_prompt in coordinator_agent.py

# ONLY replace the coordination_prompt in coordinator_agent.py

# REPLACE the coordination_prompt in coordinator_agent.py

        self.coordination_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Coordinator Agent with expertise in comprehensive telecommunications test scenario planning.

DUAL SCENARIO DETECTION EXPERTISE:
Most user stories about "eero association process" or "device setup" require testing BOTH scenarios:
- **Install Scenarios**: New customers getting eero devices for the first time
- **CoS Scenarios**: Existing customers adding, changing, or upgrading eero services

INTELLIGENT SCENARIO ANALYSIS RULES:
1. **Default to BOTH**: Unless user story is explicitly about only new installations or only service changes, plan for BOTH install AND CoS scenarios
2. **Association Process**: When user story mentions "eero association process" → Test BOTH new customer setup AND existing customer service modifications
3. **Device Setup**: When user story mentions "device setup" or "account linking" → Test BOTH new account creation AND existing account modifications
4. **Comprehensive Coverage**: Most eero-related user stories require validating the process works for BOTH new and existing customers

SCENARIO PLANNING STRATEGY:
- Always ask: "Does this process need to work for NEW customers?" (Install scenarios)
- Always ask: "Does this process need to work for EXISTING customers?" (CoS scenarios)  
- Default answer is usually YES to both questions unless explicitly stated otherwise
- Plan roughly 50/50 split between install and CoS scenarios for comprehensive coverage"""),
    
    ("human", """DUAL SCENARIO ANALYSIS:

User Story: {user_story}
Additional Requirements: {additional_requirements}
Number of Test Cases Requested: {number_of_test_cases}

Business Context: {rag_context}

COMPREHENSIVE SCENARIO DETECTION:
Analyze this user story to determine what scenarios are needed:

1. **Install Scenario Analysis**: 
   - Does this process need to work for NEW customers getting eero for the first time?
   - Are there requirements about new customer account creation or initial device setup?

2. **CoS Scenario Analysis**:
   - Does this process need to work for EXISTING customers modifying their eero services?
   - Are there requirements about existing customer account updates or service changes?

3. **Default Logic**: 
   - If user story mentions "eero association process" → Usually needs BOTH install AND CoS
   - If user story mentions "account to device association" → Usually needs BOTH new account creation AND existing account modification
   - If user story is about general "process" or "workflow" → Usually needs BOTH scenarios

SCENARIO DISTRIBUTION STRATEGY:
For {number_of_test_cases} test cases, plan appropriate distribution:
- If BOTH install and CoS needed → Split roughly 50/50 between scenarios
- Include both RESI and BUSI customer types for each scenario
- Include both truck roll variations for comprehensive coverage

CRITICAL INSTRUCTION:
Unless the user story is explicitly ONLY about new installations or ONLY about service changes, you should plan for BOTH install AND CoS scenarios.

Based on this analysis, plan requirements that cover BOTH install AND CoS scenarios:

Format: CUSTOMER_TYPE|SCENARIO_TYPE|TRUCK_ROLL_TYPE|COUNT

Example for balanced coverage:
RESI|install|No|2
RESI|install|With|2  
RESI|cos|No|2
RESI|cos|With|2
BUSI|install|No|2
BUSI|cos|No|2

Provide balanced install AND CoS requirements:""")
])
    
    async def analyze_requirements(self, user_story: str, additional_requirements: str, 
                                 number_of_test_cases: int) -> List[TestCaseRequirement]:
        """Enhanced requirement analysis with RAG context"""
        
        # Get relevant business context
        rag_context = self._get_business_context(user_story, additional_requirements)
        
        try:
            chain = self.coordination_prompt | self.llm
            response = await chain.ainvoke({
                'user_story': user_story,
                'additional_requirements': additional_requirements,
                'number_of_test_cases': number_of_test_cases,
                'rag_context': rag_context  # Include RAG context
            })
            
            # Parse simple response format
            requirements = []
            lines = response.content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if '|' in line and line.count('|') == 3:
                    try:
                        parts = line.split('|')
                        customer_type = parts[0].strip().upper()
                        scenario_type = parts[1].strip().lower()
                        truck_roll_type = parts[2].strip()
                        count = int(parts[3].strip())
                        
                        # Validate values
                        if (customer_type in ['RESI', 'BUSI'] and 
                            scenario_type in ['install', 'cos'] and 
                            truck_roll_type in ['No', 'With'] and 
                            count > 0):
                            
                            requirements.append(TestCaseRequirement(
                                customer_type=customer_type,
                                scenario_type=scenario_type,
                                truck_roll_type=truck_roll_type,
                                count_needed=count,
                                priority="high"
                            ))
                    except (ValueError, IndexError):
                        continue
            
            if not requirements:
                print("⚠️  No valid requirements parsed, using fallback")
                return self._create_fallback_requirements(user_story, number_of_test_cases)
            
            # Optimize total count
            total_count = sum(req.count_needed for req in requirements)
            if total_count != number_of_test_cases:
                requirements = self._adjust_requirements_count(requirements, number_of_test_cases)
            
            return requirements
            
        except Exception as e:
            print(f"⚠️  Enhanced coordination failed: {e}, using fallback")
            return self._create_fallback_requirements(user_story, number_of_test_cases)
    
    def _get_business_context(self, user_story: str, additional_requirements: str) -> str:
        """Get relevant business context from RAG"""
        
        if not self.rag_context:
            return "No specific business context available - using general analysis."
        
        # Extract key terms from user story
        story_text = f"{user_story} {additional_requirements}".lower()
        key_terms = [word for word in story_text.split() 
                    if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'that']]
        
        # Search for relevant contexts
        relevant_contexts = []
        for term in key_terms[:5]:  # Top 5 terms
            try:
                contexts = self.rag_context.search_context(term)
                relevant_contexts.extend(contexts[:2])  # Top 2 per term
            except:
                continue
        
        if not relevant_contexts:
            return "Standard telecommunications testing approach - no specific business context found."
        
        # Format business context
        context_text = "## BUSINESS CONTEXT INTELLIGENCE:\n\n"
        unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in relevant_contexts}
        
        for i, (filename, ctx) in enumerate(list(unique_contexts.items())[:3], 1):
            context_text += f"**Business Context {i}**:\n"
            context_text += f"- **Purpose**: {ctx.get('business_purpose', 'N/A')}\n"
            context_text += f"- **Category**: {ctx.get('test_category', 'N/A')}\n"
            context_text += f"- **Segment**: {ctx.get('customer_segment', 'N/A')}\n"
            context_text += f"- **Key Areas**: {', '.join(ctx.get('keywords', []))}\n\n"
        
        return context_text

    def _adjust_requirements_count(self, requirements: List[TestCaseRequirement], 
                                 target_count: int) -> List[TestCaseRequirement]:
        """Adjust requirements to match target count"""
        
        current_total = sum(req.count_needed for req in requirements)
        
        if current_total == target_count:
            return requirements
        elif current_total < target_count:
            # Need to add more
            deficit = target_count - current_total
            for req in requirements:
                if deficit <= 0:
                    break
                additional = min(deficit, 2)  # Max 2 additional per requirement
                req.count_needed += additional
                deficit -= additional
        else:
            # Need to reduce
            excess = current_total - target_count
            for req in requirements:
                if excess <= 0:
                    break
                if req.count_needed > 1:
                    reduction = min(excess, req.count_needed - 1)
                    req.count_needed -= reduction
                    excess -= reduction
        
        return requirements
    
    def _analyze_eero_combinations_from_story(self, user_story: str, additional_requirements: str) -> List[str]:
        """Analyze user story to detect specific eero product combinations needed"""
        
        story_text = f"{user_story} {additional_requirements}".lower()
        detected_combinations = []
        
        # Base eero detection
        if any(term in story_text for term in ['basic', 'standard', 'regular', 'base']):
            detected_combinations.append('base_eero')
        
        # Premium service detection  
        if any(term in story_text for term in ['secure', 'plus', 'premium', 'enhanced']):
            detected_combinations.append('eero_plus_secure')
        
        # Multiple devices detection
        if any(term in story_text for term in ['additional', 'multiple', 'more than', 'extra']):
            detected_combinations.append('additional_devices')
        
        # Service change detection
        if any(term in story_text for term in ['upgrade', 'change', 'modify', 'add', 'remove']):
            detected_combinations.append('service_change')
        
        # Default to base if nothing specific detected
        if not detected_combinations:
            detected_combinations.append('comprehensive_coverage')
        
        return detected_combinations

    # ADD this section to the _create_fallback_requirements method in coordinator_agent.py
    # MODIFY the existing fallback method with this enhanced logic:

    def _create_fallback_requirements(self, user_story: str, count: int) -> List[TestCaseRequirement]:
        """Create enhanced fallback with mandatory dual scenario coverage"""
        
        print(f"🔧 Creating dual scenario fallback for {count} test cases...")
        
        story_lower = user_story.lower()
        
        # ENHANCED DUAL SCENARIO DETECTION
        # Default to BOTH scenarios unless explicitly single-scenario
        needs_install = True  # Default to YES
        needs_cos = True      # Default to YES
        
        # Only exclude install if explicitly ONLY about existing customers
        if any(phrase in story_lower for phrase in [
            'only existing', 'existing customers only', 'current customers only'
        ]):
            needs_install = False
            
        # Only exclude CoS if explicitly ONLY about new customers  
        if any(phrase in story_lower for phrase in [
            'only new', 'new customers only', 'first time only'
        ]):
            needs_cos = False
        
        # FORCE BOTH if general process mentioned
        if any(phrase in story_lower for phrase in [
            'eero association process', 'association process', 'device setup', 
            'account linking', 'process built', 'enable association'
        ]):
            needs_install = True
            needs_cos = True
            print("   🎯 Detected general process - forcing BOTH install AND CoS coverage")
        
        # Customer type detection (default to both)
        needs_resi = True
        needs_busi = True
        
        if 'residential only' in story_lower or 'resi only' in story_lower:
            needs_busi = False
        if 'business only' in story_lower or 'commercial only' in story_lower:
            needs_resi = False
        
        # Build comprehensive requirements
        requirements = []
        scenarios = []
        customers = []
        
        if needs_install:
            scenarios.append('install')
        if needs_cos:
            scenarios.append('cos')
            
        if needs_resi:
            customers.append('RESI')
        if needs_busi:
            customers.append('BUSI')
        
        truck_types = ['No', 'With']
        
        # BALANCED DISTRIBUTION across install AND CoS
        total_combinations = len(scenarios) * len(customers) * len(truck_types)
        base_count = max(1, count // total_combinations)
        remaining_count = count
        
        print(f"   📊 Planning: {len(scenarios)} scenarios x {len(customers)} customers x {len(truck_types)} truck types")
        
        for scenario in scenarios:
            for customer in customers:
                for truck in truck_types:
                    if remaining_count > 0:
                        use_count = min(base_count, remaining_count)
                        if use_count > 0:
                            requirements.append(TestCaseRequirement(
                                customer_type=customer,
                                scenario_type=scenario,
                                truck_roll_type=truck,
                                count_needed=use_count,
                                priority="high"
                            ))
                            remaining_count -= use_count
                            print(f"   ✅ {customer} {scenario} - {truck} truck roll (x{use_count})")
        
        # Distribute any remaining count
        if remaining_count > 0 and requirements:
            requirements[0].count_needed += remaining_count
            print(f"   📈 Added {remaining_count} extra to {requirements[0].customer_type} {requirements[0].scenario_type}")
        
        # VALIDATION: Ensure both scenarios are represented
        scenario_types = [req.scenario_type for req in requirements]
        if needs_install and 'install' not in scenario_types:
            print("   ⚠️  WARNING: Install scenarios missing from fallback!")
        if needs_cos and 'cos' not in scenario_types:
            print("   ⚠️  WARNING: CoS scenarios missing from fallback!")
        
        return requirements