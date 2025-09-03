from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCaseRequirement
from combination_detector import EeroCombinationDetector

class CoordinatorAgent:
    """Hybrid Coordinator: Uses EeroCombinationDetector intelligence + GPT parsing"""
    
    def __init__(self, llm: AzureChatOpenAI, rag_context=None):
        self.llm = llm
        self.rag_context = rag_context
        self.combination_detector = EeroCombinationDetector()
        
        # Enhanced coordination prompt that uses combination intelligence
        self.coordination_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a test case requirement coordinator with access to business intelligence about eero combinations.

EERO SERVICE COMBINATIONS:
You have access to 28 predefined eero service combinations that cover:
- Install scenarios: New customers getting eero service (IDs 1-12)
- Change of Service: Existing customers modifying eero service (IDs 13-28)
- IDs 29, 30, 31 are Important combinations which need to be generated.
- Customer types: Residential (RESI) and Business (BUSI)
- Truck roll: With technician or No truck (self-install)
- Service types: Eero, Eero Plus, Additional devices, Device removal

CRITICAL MISSING COMBINATIONS (High Priority):
- ID 29: BUSI CoS - HSD customer with Eero and additional Eero Business Remove Eero device which is gateway No - No truck
- ID 30: BUSI CoS - HSD customer with Eero and additional Eero Business Remove Eero device which is gateway Yes - No truck  
- ID 31: BUSI CoS - HSD customer with Eero and additional Eero Business Remove entire Eero service along with devices - No truck

These device removal scenarios are CRITICAL for comprehensive device lifecycle and association testing.
When you detect BUSI-cos-NoTruck requirements, prioritize these missing device management scenarios.

SERVICE CODE MAPPING:
- RESI customers: HE008 (Eero), HE009 (Eero plus), HE015 (Eero secure plus/Eero additional)
- BUSI CoS: BHSY5 (Eero W2W), BHSY6 (Eero Additional)

YOUR TASK:
Based on the detected combinations and story analysis provided, generate the appropriate test case requirements."""),
            
            ("human", """**USER STORY:**
{user_story}

**INTELLIGENT ANALYSIS RESULTS:**
- Story suggests {intelligent_count} test cases are needed
- Story analysis: {story_analysis}
- Detected {num_combinations} relevant combinations from the predefined list

**RELEVANT COMBINATIONS FOUND:**
{relevant_combinations}

**CRITICAL CUSTOMER STATUS DISTINCTION:**
When analyzing BUSI-cos-NoTruck requirements, distinguish between:
- Basic Eero customers (existing_hsd_eero) - customers with standard Eero setup
- Eero + Additional customers (existing_hsd_eero_additional) - customers with MULTIPLE Eero devices

IDs 29-31 specifically require "existing_hsd_eero_additional" customers - those with complex multi-device setups.

**INSTRUCTIONS:**
Based on this intelligence, generate test case requirements that:
1. Use the detected combinations as guidance
2. Distinguish between basic vs additional device customer scenarios
3. Focus on the {intelligent_count} most relevant scenarios including missing IDs 29-31
4. Ensure coverage of both simple and complex customer device setups

**OUTPUT FORMAT:**
For each requirement needed, specify:
CUSTOMER_TYPE|SCENARIO_TYPE|TRUCK_ROLL_TYPE|COUNT_NEEDED|PRIORITY

Where:
- CUSTOMER_TYPE: RESI or BUSI
- SCENARIO_TYPE: install or cos
- TRUCK_ROLL_TYPE: With or No
- COUNT_NEEDED: number (make total equal {intelligent_count})
- PRIORITY: high, medium, or low

Generate {intelligent_count} total test cases across all requirements.""")
        ])
    
    async def analyze_requirements(self, user_story: str, additional_requirements: str, 
                                 number_of_test_cases: int = None) -> List[TestCaseRequirement]:
        """Hybrid analysis: Use combination detector intelligence + GPT parsing"""
        
        print(f"    Analyzing user story with hybrid approach (business intelligence + GPT)...")
        
        # Step 1: Use combination detector for intelligent analysis
        print(f"    Using EeroCombinationDetector for business intelligence...")
        
        # Get intelligent count from story analysis (ignore user input for now)
        intelligent_count = self.combination_detector.determine_test_case_count(user_story)
        
        # Use the intelligently detected count, or fall back to user request
        if number_of_test_cases:
            final_count = number_of_test_cases
            print(f"    User requested: {number_of_test_cases}, Intelligence suggests: {intelligent_count}, Using: {final_count}")
        else:
            final_count = intelligent_count
            print(f"    Intelligence-based count: {final_count}")
        
        # Get combination intelligence
        detected_combinations = self.combination_detector.detect_combinations_from_story(
            user_story, final_count
        )
        
        # Get story analysis
        story_analysis = self.combination_detector._analyze_user_story(user_story.lower())
        
        # Step 2: If we have good combination matches, use combination detector directly
        if detected_combinations and len(detected_combinations) > 0:
            # Check if combinations are relevant (high scores)
            high_score_combos = [c for c in detected_combinations if c['match_score'] > 0.6]
            
            if high_score_combos:
                print(f"    Using combination detector results directly ({len(high_score_combos)} high-relevance combinations)")
                return self.combination_detector.get_combination_requirements(detected_combinations[:final_count])
        
        # Step 3: Use GPT with combination intelligence as context
        print(f"    Using GPT with combination intelligence as context...")
        
        try:
            # Format relevant combinations for GPT
            combinations_text = self._format_combinations_for_gpt(detected_combinations[:10])  # Top 10 for context
            
            # Use LLM with business intelligence
            chain = self.coordination_prompt | self.llm
            response = await chain.ainvoke({
                'user_story': user_story,
                'intelligent_count': final_count,
                'story_analysis': str(story_analysis),
                'num_combinations': len(detected_combinations),
                'relevant_combinations': combinations_text
            })
            
            # Parse the GPT response
            requirements = self._parse_llm_response(response.content, final_count)
            
            if not requirements:
                print("    GPT analysis failed, using combination detector fallback")
                # Fallback to combination detector
                if detected_combinations:
                    return self.combination_detector.get_combination_requirements(detected_combinations[:final_count])
                else:
                    return self._create_intelligent_fallback(story_analysis, final_count)
            
            # Validate total count
            total_needed = sum(req.count_needed for req in requirements)
            if total_needed != final_count:
                print(f"    Adjusting counts: needed {final_count}, got {total_needed}")
                requirements = self._adjust_counts(requirements, final_count)
            
            print(f"    Generated {len(requirements)} requirement types for {final_count} total test cases")
            return requirements
            
        except Exception as e:
            print(f"    Hybrid coordination failed: {e}, using combination detector fallback")
            if detected_combinations:
                return self.combination_detector.get_combination_requirements(detected_combinations[:final_count])
            else:
                return self._create_intelligent_fallback(story_analysis, final_count)
    
    def _format_combinations_for_gpt(self, combinations: list) -> str:
        """Format detected combinations for GPT context"""
        if not combinations:
            return "No specific combinations detected"
        
        text = ""
        for i, detection in enumerate(combinations[:8], 1):  # Top 8 for context
            combo = detection['combination']
            score = detection['match_score']
            text += f"{i}. ID {combo['id']}: {combo['description']} (relevance: {score:.2f})\n"
        
        return text
    
    def _parse_llm_response(self, response: str, target_count: int) -> List[TestCaseRequirement]:
        """Parse LLM response into TestCaseRequirement objects"""
        requirements = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if '|' in line and line.count('|') >= 4:
                try:
                    parts = line.split('|')
                    customer_type = parts[0].strip().upper()
                    scenario_type = parts[1].strip().lower()
                    truck_roll_type = parts[2].strip().title()
                    count_needed = int(parts[3].strip()) if len(parts) > 3 else 1
                    priority = parts[4].strip().lower() if len(parts) > 4 else 'medium'
                    
                    if (customer_type in ['RESI', 'BUSI'] and 
                        scenario_type in ['install', 'cos'] and 
                        truck_roll_type in ['With', 'No'] and 
                        count_needed > 0 and
                        priority in ['high', 'medium', 'low']):
                        
                        req = TestCaseRequirement(
                            customer_type=customer_type,
                            scenario_type=scenario_type,
                            truck_roll_type=truck_roll_type,
                            count_needed=count_needed,
                            priority=priority
                        )
                        requirements.append(req)
                        
                except (ValueError, IndexError) as e:
                    print(f"    Skipping invalid line: {line} ({e})")
                    continue
        
        return requirements
    
    def _create_intelligent_fallback(self, story_analysis: dict, count: int) -> List[TestCaseRequirement]:
        """Create intelligent fallback using story analysis"""
        print(f"    Creating intelligent fallback for {count} test cases...")
        
        # Use story analysis to create requirements
        customer_types = []
        if 'residential' in story_analysis.get('customer_segments', []):
            customer_types.append('RESI')
        if 'business' in story_analysis.get('customer_segments', []):
            customer_types.append('BUSI')
        if not customer_types:
            customer_types = ['RESI', 'BUSI']
        
        scenarios = []
        if 'install' in story_analysis.get('order_types', []):
            scenarios.append('install')
        if 'cos' in story_analysis.get('order_types', []):
            scenarios.append('cos')
        if not scenarios:
            scenarios = ['cos']  # Default to cos for most stories
        
        # Create balanced requirements
        requirements = []
        combinations = []
        for customer_type in customer_types:
            for scenario in scenarios:
                combinations.append((customer_type, scenario, 'No'))
                if count > len(customer_types) * len(scenarios):
                    combinations.append((customer_type, scenario, 'With'))
        
        # Distribute count
        base_count = count // len(combinations)
        remainder = count % len(combinations)
        
        for i, (customer_type, scenario_type, truck_roll_type) in enumerate(combinations):
            req_count = base_count + (1 if i < remainder else 0)
            if req_count > 0:
                # Higher priority for association-related stories
                priority = 'high' if story_analysis.get('association_process_detected') else 'medium'
                
                req = TestCaseRequirement(
                    customer_type=customer_type,
                    scenario_type=scenario_type,
                    truck_roll_type=truck_roll_type,
                    count_needed=req_count,
                    priority=priority
                )
                requirements.append(req)
        
        return requirements
    
    def _adjust_counts(self, requirements: List[TestCaseRequirement], target_count: int) -> List[TestCaseRequirement]:
        """Adjust requirement counts to match target"""
        current_total = sum(req.count_needed for req in requirements)
        
        if current_total == target_count:
            return requirements
        
        if current_total < target_count:
            # Add more to high priority requirements first
            deficit = target_count - current_total
            high_priority = [req for req in requirements if req.priority == 'high']
            targets = high_priority if high_priority else requirements
            
            for i in range(deficit):
                req_index = i % len(targets)
                targets[req_index].count_needed += 1
        else:
            # Remove from low priority requirements first
            excess = current_total - target_count
            low_priority = [req for req in requirements if req.priority == 'low']
            targets = low_priority if low_priority else requirements
            
            for i in range(excess):
                req_index = i % len(targets)
                if targets[req_index].count_needed > 1:
                    targets[req_index].count_needed -= 1
        
        return requirements