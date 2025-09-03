from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class RetrievalAgent:
    """Simplified Retrieval Agent with clear matching logic and service normalization"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context=None):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        
        # Service equivalency mappings - inline to avoid extra files
        self.service_equivalents = {
            'basic_eero': ['basic', 'eero', 'standard', 'base', 'he008', 'regular', 'hsd along with eero'],
            'eero_plus': ['plus', 'eero plus', 'premium', 'he009', 'enhanced'],
            'eero_secure': ['secure', 'secure plus', 'eero secure plus', 'he015', 'additional']
        }
        
        # Simple selection prompt for GPT when needed
        self.selection_prompt = ChatPromptTemplate.from_messages([
            ("system", """You help select the best test cases from available options.

Your job is to pick the most relevant test cases based on:
1. Exact customer type match (RESI/BUSI)
2. Exact scenario match (install/cos)  
3. Exact truck roll match (With/No)
4. Most detailed test cases (more steps is better)
5. Complete workflows with validations

Always prefer test cases with more steps as they are more comprehensive."""),
            
            ("human", """Need to find test cases for:
- Customer Type: {customer_type}
- Scenario: {scenario_type}
- Truck Roll: {truck_roll_type}
- Count Needed: {count_needed}

Available test cases:
{available_cases}

Please select the {count_needed} best matching test case IDs from the list above.
Just return the test case IDs, one per line.""")
        ])

    async def find_test_cases(self, requirement: TestCaseRequirement, user_story: str) -> List[TestCase]:
        """Find matching test cases with improved matching logic and descriptive name awareness"""
        
        # Check if this is a descriptive requirement with specific scenario needs
        descriptive_name = getattr(requirement, 'descriptive_name', '')
        is_specific_scenario = any(keyword in descriptive_name for keyword in [
            'RemoveDeviceGatewayNo', 'RemoveDeviceGatewayYes', 'RemoveEeroServiceDevice'
        ])
        
        if is_specific_scenario:
            print(f"    Searching for specific scenario: {descriptive_name}")
            return await self._find_specific_scenario_matches(requirement, descriptive_name)
        else:
            print(f"    Searching for {requirement.customer_type} {requirement.scenario_type} {requirement.truck_roll_type} test cases...")
        
        # Find exact matches first - EXCLUDE generated test cases and empty files
        exact_matches = [
            tc for tc in self.test_cases
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated and
                not tc.id.startswith('TC_GEN_') and  # Filter generated cases
                len(tc.steps) > 0 and  # Filter empty test cases
                tc.content and len(tc.content.strip()) > 10)  # Filter essentially empty files
        ]
        
        # If no exact matches, try flexible matching with truck roll variations
        if not exact_matches:
            print(f"    No exact matches, trying flexible truck roll matching...")
            flexible_matches = [
                tc for tc in self.test_cases
                if (tc.customer_type == requirement.customer_type and
                    tc.scenario_type == requirement.scenario_type and
                    not tc.is_generated and
                    not tc.id.startswith('TC_GEN_') and
                    len(tc.steps) > 0 and
                    tc.content and len(tc.content.strip()) > 10)
            ]
            
            if flexible_matches:
                print(f"    Found {len(flexible_matches)} flexible matches (different truck roll types)")
                exact_matches = flexible_matches
        
        if not exact_matches:
            print(f"    No exact matches found")
            return []
        
        print(f"    Found {len(exact_matches)} exact matches")
        
        # Sort by number of steps (more detailed first) - handle None values safely
        exact_matches.sort(key=lambda tc: len(tc.steps) if tc.steps else 0, reverse=True)
        
        # If we have enough matches, return them
        if len(exact_matches) >= requirement.count_needed:
            selected = exact_matches[:requirement.count_needed]
            print(f"    Selected {len(selected)} test cases:")
            for tc in selected:
                step_count = len(tc.steps) if tc.steps else 0
                print(f"      {tc.id}: {step_count} steps")
            return selected
        
        # If we need LLM help to choose from many options
        if len(exact_matches) > requirement.count_needed * 2:
            print(f"    Using LLM to select best from {len(exact_matches)} options")
            return await self._llm_selection(exact_matches, requirement)
        
        # Return all exact matches if we have fewer than needed
        print(f"    Returning all {len(exact_matches)} exact matches")
        for tc in exact_matches:
            step_count = len(tc.steps) if tc.steps else 0
            print(f"      {tc.id}: {step_count} steps")
        return exact_matches

    async def _llm_selection(self, candidates: List[TestCase], requirement: TestCaseRequirement) -> List[TestCase]:
        """Use LLM to select best test cases from candidates"""
        
        # Format candidates for LLM
        available_cases_text = ""
        for tc in candidates:
            step_count = len(tc.steps) if tc.steps else 0
            available_cases_text += f"{tc.id}: {tc.title} ({step_count} steps)\n"
            content_preview = tc.content[:200] if tc.content else "No content"
            available_cases_text += f"  Content preview: {content_preview}...\n\n"
        
        try:
            chain = self.selection_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type, 
                'truck_roll_type': requirement.truck_roll_type,
                'count_needed': requirement.count_needed,
                'available_cases': available_cases_text
            })
            
            # Parse selected IDs
            selected_ids = [line.strip() for line in response.content.strip().split('\n') 
                          if line.strip()]
            
            # Find selected test cases
            selected_cases = []
            for tc_id in selected_ids:
                for tc in candidates:
                    if tc.id == tc_id and tc not in selected_cases:
                        selected_cases.append(tc)
                        break
            
            if len(selected_cases) >= requirement.count_needed:
                result = selected_cases[:requirement.count_needed]
                print(f"    LLM selected {len(result)} test cases")
                return result
            else:
                # Fallback to top candidates by step count
                result = candidates[:requirement.count_needed]
                print(f"    LLM selection failed, using top {len(result)} by step count")
                return result
                
        except Exception as e:
            print(f"    LLM selection failed: {e}, using top candidates")
            return candidates[:requirement.count_needed]

    def get_available_test_case_types(self) -> dict:
        """Get breakdown of available test case types"""
        breakdown = {}
        
        for tc in self.test_cases:
            if not tc.is_generated:
                key = f"{tc.customer_type}-{tc.scenario_type}-{tc.truck_roll_type}Truck"
                breakdown[key] = breakdown.get(key, 0) + 1
        
        return breakdown
    
    def _are_services_equivalent(self, title1: str, title2: str) -> bool:
        """Check if two test case titles represent equivalent services"""
        title1_lower = title1.lower()
        title2_lower = title2.lower()
        
        # Check if both refer to the same basic service type
        for service_type, variants in self.service_equivalents.items():
            title1_matches = any(variant in title1_lower for variant in variants)
            title2_matches = any(variant in title2_lower for variant in variants)
            
            if title1_matches and title2_matches:
                return True
        
        return False
    
    def _normalize_truck_roll(self, truck_roll: str) -> str:
        """Normalize truck roll type for better matching"""
        truck_lower = truck_roll.lower()
        
        if any(word in truck_lower for word in ['with', 'truck', 'roll', 'technician']):
            if 'no' not in truck_lower and 'without' not in truck_lower:
                return 'With'
        
        return 'No'
    
    async def _find_specific_scenario_matches(self, requirement: TestCaseRequirement, descriptive_name: str) -> List[TestCase]:
        """Find test cases that match exact combination descriptions to avoid confusion with generic scenarios"""
        
        # Get the exact combination description if available
        exact_description = getattr(requirement, 'exact_combination_description', '')
        
        # For the 3 critical missing combinations, use exact description matching
        critical_missing_patterns = [
            "Change of Service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero device which is gateway No",
            "Change of Service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero device which is gateway Yes", 
            "Change of service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero service along with Device"
        ]
        
        # Check if this is one of the 3 critical missing scenarios
        is_critical_missing = any(pattern.lower() in exact_description.lower() for pattern in critical_missing_patterns)
        
        if is_critical_missing:
            print(f"    This is a critical missing scenario that needs generation!")
            print(f"    Exact combination needed: {exact_description}")
            print(f"    Searching for exact match in existing test cases...")
            
            # Search for exact combination description match
            for tc in self.test_cases:
                if (tc.customer_type == requirement.customer_type and
                    tc.scenario_type == requirement.scenario_type and
                    tc.truck_roll_type == requirement.truck_roll_type and
                    not tc.is_generated and
                    not tc.id.startswith('TC_GEN_') and
                    len(tc.steps) > 0 and
                    tc.content and len(tc.content.strip()) > 10):
                    
                    # Check if test case matches the exact combination description
                    title_lower = tc.title.lower() if tc.title else ""
                    content_lower = tc.content.lower() if tc.content else ""
                    combined_text = f"{title_lower} {content_lower}"
                    
                    # Look for key distinguishing phrases that match exact combination
                    required_phrases = ["additional eero", "business", "existing hsd customer with eero"]
                    if all(phrase in combined_text for phrase in required_phrases):
                        print(f"    Found potential exact match: {tc.id}")
                        return [tc]
            
            print(f"    No exact combination match found - forcing generation!")
            return []  # Force generation for missing critical scenarios
        
        # For non-critical scenarios, use the original pattern matching
        else:
            return await self._find_generic_scenario_matches(requirement, descriptive_name)
    
    async def _find_generic_scenario_matches(self, requirement: TestCaseRequirement, descriptive_name: str) -> List[TestCase]:
        """Original pattern matching logic for non-critical scenarios"""
        
        # Extract scenario keywords and search patterns  
        scenario_patterns = {
            'RemoveDeviceGatewayNo': ['gateway no', 'gateway \'no\'', 'not gateway', 'non-gateway'],
            'RemoveDeviceGatewayYes': ['gateway yes', 'gateway \'yes\'', 'is gateway', 'main gateway'],
            'RemoveEeroServiceDevice': ['removing eero service', 'remove eero service', 'service along with device', 'entire eero service']
        }
        
        # Determine which specific scenario we're looking for
        target_patterns = []
        scenario_type = None
        for scenario_key, patterns in scenario_patterns.items():
            if scenario_key in descriptive_name:
                target_patterns = patterns
                scenario_type = scenario_key
                break
        
        if not target_patterns:
            print(f"    No specific patterns found for: {descriptive_name}")
            return []
        
        print(f"    Looking for scenario: {scenario_type}")
        print(f"    Search patterns: {target_patterns}")
        
        # Search for test cases that match the specific scenario
        specific_matches = []
        for tc in self.test_cases:
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated and
                not tc.id.startswith('TC_GEN_') and
                len(tc.steps) > 0 and
                tc.content and len(tc.content.strip()) > 10):
                
                # Check if test case title/content matches any of the specific patterns
                title_lower = tc.title.lower() if tc.title else ""
                content_lower = tc.content.lower() if tc.content else ""
                combined_text = f"{title_lower} {content_lower}"
                
                if any(pattern in combined_text for pattern in target_patterns):
                    specific_matches.append(tc)
                    print(f"    Found specific match: {tc.id}")
        
        if specific_matches:
            print(f"    Found {len(specific_matches)} specific scenario matches")
            # Sort by step count (more detailed first)
            specific_matches.sort(key=lambda tc: len(tc.steps) if tc.steps else 0, reverse=True)
            return specific_matches[:requirement.count_needed]
        else:
            print(f"    No specific scenario matches found - this scenario needs generation!")
            # Return empty to trigger generation
            return []