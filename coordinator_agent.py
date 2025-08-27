from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCaseRequirement
from combination_detector import EeroCombinationDetector

class CoordinatorAgent:
    """Enhanced Coordinator Agent with understanding summary and better combination detection"""
    
    def __init__(self, llm: AzureChatOpenAI, rag_context=None):
        self.llm = llm
        self.rag_context = rag_context
        self.combination_detector = EeroCombinationDetector()
        
        # Simplified coordination prompt focused on core requirements
        self.coordination_prompt = ChatPromptTemplate.from_messages([
            ("system", """You coordinate test case requirements using intelligent combination detection for Cable One eero services.

**AVAILABLE PREDEFINED COMBINATIONS:**
There are 31 predefined eero test combinations (IDs 1-31):
- IDs 1-28: ALREADY EXIST in test case library (can be retrieved)
- IDs 29-31: MISSING and need to be GENERATED (high priority device removal scenarios)

**MISSING HIGH-PRIORITY COMBINATIONS (MUST GENERATE):**
- ID 29: BUSI CoS remove device (not gateway) - BHSY5/BHSY6 
- ID 30: BUSI CoS remove device (gateway) - BHSY5/BHSY6
- ID 31: BUSI CoS remove eero service + device - BHSY5/BHSY6

**COMBINATION CATEGORIES:**
1. **Install New Residential** (IDs 1-8): Basic eero, eero plus, additional devices
2. **Install New Business** (IDs 9-12): Business eero setups  
3. **CoS Existing Residential** (IDs 13-24): Add/remove eero services, device management
4. **CoS Existing Business** (IDs 25-31): Business change of service scenarios

**USER STORY INTELLIGENCE:**
**Device Association/Account Linking Stories:**
- Keywords: "association", "account to device", "binding", "partner account"
- Requires: COMPREHENSIVE device lifecycle testing (install + removal scenarios)
- Prioritize: Missing combinations 29-31 for complete lifecycle coverage
- Include: Both RESI and BUSI scenarios for business requirement completeness

**CRITICAL BUSINESS RULES:**
- BUSI CoS scenarios: ONLY BHSY5 (Eero W2W) or BHSY6 (Eero Additional)
- RESI scenarios: HE008 (basic), HE009 (plus), HE015 (secure plus)
- Association processes require device removal testing (IDs 29-31)

**YOUR TASK:**
Analyze the user story and intelligently select from the 31 predefined combinations, prioritizing missing ones (29-31) when device lifecycle is indicated."""),
            
            ("human", """**USER STORY:** {user_story}

**ADDITIONAL REQUIREMENTS:** {additional_requirements}

**REQUESTED TEST CASES:** {number_of_test_cases}

**BUSINESS CONTEXT:** {rag_context}

**TASK:**
1. Analyze the user story to understand what types of test cases are needed
2. Create {number_of_test_cases} diverse, unique combinations
3. Balance RESI/BUSI customers and Install/CoS scenarios
4. Include variety in eero types and truck roll approaches

**ANALYSIS:**
What does this user story need?
- Customer types: RESI, BUSI, or both?
- Scenarios: Install (new customers), CoS (existing customers), or both?
- Eero types: basic, plus, additional devices, device removal, or mixed?
- Truck roll: With technician, No truck (self-install), or both?
- Device lifecycle: Does story mention removal, association, or device management?

**IMPORTANT CONSTRAINTS:**
- If BUSI CoS needed: Only use eero types that work with BHSY5/BHSY6 (W2W, Additional)
- If device management/removal mentioned: Include removal scenarios (IDs 29-31)
- Ensure diversity: Don't repeat the same combination multiple times

**OUTPUT FORMAT:**
CUSTOMER_TYPE|SCENARIO_TYPE|TRUCK_ROLL_TYPE|EERO_TYPE|COUNT|PRIORITY

**EXAMPLES:**
RESI|install|With|eero|2|HIGH
BUSI|cos|No|eero_plus|1|MEDIUM
RESI|cos|No|eero_additional|1|MEDIUM

**REQUIREMENTS:**
- Each combination must be unique
- Total count must equal {number_of_test_cases}
- Balance customer types and scenarios
- Include variety in eero types and truck roll
- Provide priority level (HIGH/MEDIUM/LOW)

Generate {number_of_test_cases} diverse requirements now:""")
        ])
    
    async def analyze_requirements(self, user_story: str, additional_requirements: str, 
                                 number_of_test_cases: int = None) -> List[TestCaseRequirement]:
        """Enhanced analysis using intelligent combination detection"""
        
        print(f"    Analyzing story with intelligent combination detection...")
        
        # Use combination detector to find relevant combinations with intelligent count detection
        print(f"    Detecting relevant combinations from predefined list...")
        detected_combinations = self.combination_detector.detect_combinations_from_story(
            user_story + " " + additional_requirements, 
            number_of_test_cases  # Will be auto-determined if None
        )
        
        if detected_combinations:
            # Determine final count from detected combinations if not provided
            final_count = number_of_test_cases or len([d for d in detected_combinations if d['match_score'] > 0.4])
            final_count = min(final_count, len(detected_combinations))
            
            print(f"    Found {len(detected_combinations)} relevant combinations:")
            print(f"    Selecting top {final_count} combinations:")
            for detection in detected_combinations[:final_count]:
                combo = detection["combination"]
                print(f"      - ID {combo['id']}: {combo['description']} (score: {detection['match_score']:.2f})")
            
            # Convert to TestCaseRequirement format
            requirements = self.combination_detector.get_combination_requirements(
                detected_combinations[:final_count]
            )
            
        else:
            print(f"    No specific combinations detected, using LLM-guided analysis...")
            # Fallback to LLM analysis with combination context
            # Use intelligent count determination for LLM fallback too
            fallback_count = number_of_test_cases or self.combination_detector.determine_test_case_count(user_story)
            requirements = await self._llm_guided_analysis(
                user_story, additional_requirements, fallback_count
            )
        
        # Validate diversity and enhance
        diversity_check = self._check_requirement_diversity(requirements)
        print(f"    Diversity check: {diversity_check}")
        
        # Adjust count only if a specific count was requested
        if number_of_test_cases and len(requirements) != number_of_test_cases:
            requirements = self._adjust_requirements_count(requirements, number_of_test_cases)
        
        print(f"    Generated {len(requirements)} intelligent requirements from predefined combinations")
        return requirements
    
    async def _llm_guided_analysis(self, user_story: str, additional_requirements: str, 
                                   number_of_test_cases: int) -> List[TestCaseRequirement]:
        """Fallback LLM analysis when combination detector doesn't find matches"""
        try:
            rag_context_text = self._get_rag_context_for_coordination(user_story, additional_requirements)
            combination_analysis = self._get_combination_analysis_from_rag(user_story)
            
            chain = self.coordination_prompt | self.llm
            response = await chain.ainvoke({
                'user_story': user_story,
                'additional_requirements': additional_requirements,
                'number_of_test_cases': number_of_test_cases,
                'rag_context': rag_context_text,
                'combination_analysis': self._format_combination_analysis(combination_analysis)
            })
            
            requirements = self._parse_diverse_requirements(response.content, combination_analysis)
            
            if not requirements:
                requirements = self._create_diverse_fallback(user_story, combination_analysis, number_of_test_cases)
                
            return requirements
            
        except Exception as e:
            print(f"    LLM guided analysis failed: {e}, using diverse fallback")
            return self._create_diverse_fallback(user_story, {}, number_of_test_cases)
    
    def _extract_understanding_summary(self, response_content: str) -> List[str]:
        """Extract LLM understanding summary from response"""
        lines = response_content.split('\n')
        summary_lines = []
        
        in_summary = False
        for line in lines:
            if 'understanding summary' in line.lower():
                in_summary = True
                continue
            elif in_summary:
                if line.strip() and not line.startswith('**STEP'):
                    if any(marker in line for marker in ['##', 'CUSTOMER_TYPE', '---']):
                        break
                    summary_lines.append(line.strip())
        
        return summary_lines[:6]  # First 6 lines of summary
    
    def _parse_diverse_requirements(self, response_content: str, combination_analysis: dict) -> List[TestCaseRequirement]:
        """Parse requirements with diversity enforcement"""
        requirements = []
        lines = response_content.strip().split('\n')
        seen_combinations = set()
        
        for line in lines:
            line = line.strip()
            if '|' in line and line.count('|') >= 4:
                try:
                    parts = line.split('|')
                    customer_type = parts[0].strip().upper()
                    scenario_type = parts[1].strip().lower()
                    truck_roll_type = parts[2].strip().title()
                    eero_type = parts[3].strip().lower() if len(parts) > 3 else 'eero'
                    count = int(parts[4].strip()) if len(parts) > 4 else 1
                    priority = parts[5].strip().upper() if len(parts) > 5 else 'MEDIUM'
                    
                    # Create combination signature for diversity check
                    combo_signature = f"{customer_type}-{scenario_type}-{truck_roll_type}-{eero_type}"
                    
                    if (customer_type in ['RESI', 'BUSI'] and 
                        scenario_type in ['install', 'cos'] and 
                        truck_roll_type in ['No', 'With'] and 
                        count > 0 and
                        priority in ['HIGH', 'MEDIUM', 'LOW'] and
                        combo_signature not in seen_combinations):  # Diversity check
                        
                        req = TestCaseRequirement(
                            customer_type=customer_type,
                            scenario_type=scenario_type,
                            truck_roll_type=truck_roll_type,
                            count_needed=count,
                            priority=priority.lower()
                        )
                        
                        req.eero_type = eero_type
                        requirements.append(req)
                        seen_combinations.add(combo_signature)
                        
                except (ValueError, IndexError):
                    continue
        
        return requirements
    
    def _check_requirement_diversity(self, requirements: List[TestCaseRequirement]) -> dict:
        """Check diversity of generated requirements"""
        diversity = {
            "customer_types": set(),
            "scenario_types": set(),
            "truck_roll_types": set(),
            "eero_types": set(),
            "unique_combinations": len(requirements)
        }
        
        for req in requirements:
            diversity["customer_types"].add(req.customer_type)
            diversity["scenario_types"].add(req.scenario_type)
            diversity["truck_roll_types"].add(req.truck_roll_type)
            diversity["eero_types"].add(getattr(req, 'eero_type', 'eero'))
        
        return {
            "customer_variety": len(diversity["customer_types"]),
            "scenario_variety": len(diversity["scenario_types"]),
            "truck_variety": len(diversity["truck_roll_types"]),
            "eero_variety": len(diversity["eero_types"]),
            "total_unique": diversity["unique_combinations"],
            "is_diverse": len(diversity["customer_types"]) > 1 or len(diversity["scenario_types"]) > 1
        }
    
    def _create_diverse_fallback(self, user_story: str, combination_analysis: dict, 
                               count: int) -> List[TestCaseRequirement]:
        """Create diverse fallback ensuring variety and correct count"""
        
        print(f" Creating diverse fallback with variety enforcement for {count} test cases...")
        
        # Check if this is a device removal focused story
        specific_scenarios = combination_analysis.get('specific_scenarios', [])
        is_removal_focus = 'removal' in specific_scenarios
        
        if is_removal_focus:
            print("    Device removal story detected - prioritizing missing combinations IDs 29-31")
            # PRIORITY: Missing business device removal scenarios (IDs 29-31) come FIRST
            base_combinations = [
                ("BUSI", "cos", "No", "remove_device_not_gateway", "high"),
                ("BUSI", "cos", "No", "remove_device_gateway", "high"),
                ("BUSI", "cos", "No", "remove_eero_along_device", "high"),
                # Additional combinations for higher counts
                ("RESI", "cos", "No", "remove_device_not_gateway", "high"),
                ("RESI", "cos", "No", "remove_device_gateway", "high"), 
                ("RESI", "cos", "No", "remove_eero_along_device", "high"),
                ("BUSI", "cos", "With", "eero_plus", "medium"),
                ("RESI", "install", "With", "eero", "medium"),
            ]
        else:
            # Default diverse combinations with correct BUSI CoS types
            base_combinations = [
                ("RESI", "install", "With", "eero", "high"),
                ("RESI", "cos", "No", "eero_plus", "medium"),
                ("BUSI", "install", "With", "eero", "medium"),
                ("RESI", "install", "No", "eero_additional", "medium"),
                # PRIORITY: Missing business device removal scenarios (IDs 29-31)
                ("BUSI", "cos", "No", "remove_device_not_gateway", "high"),
                ("BUSI", "cos", "No", "remove_device_gateway", "high"),
                ("BUSI", "cos", "No", "remove_eero_along_device", "high"),
            # Extended combinations for higher counts - CORRECTED BUSI CoS
            ("BUSI", "install", "No", "eero_additional", "low"),
            ("RESI", "cos", "With", "eero", "medium"),
            ("BUSI", "install", "With", "eero_plus", "low"),
            ("RESI", "install", "With", "eero_plus", "low"),
            ("BUSI", "cos", "No", "eero_additional", "low"),  # Valid: additional devices
            ("RESI", "cos", "No", "eero_additional", "low"),
            ("BUSI", "install", "No", "eero", "low"),
            ("RESI", "cos", "With", "eero_plus", "low"),
        ]
        
        requirements = []
        
        if count <= len(base_combinations):
            # Use first 'count' combinations with count_needed=1
            selected_combinations = base_combinations[:count]
            for customer_type, scenario_type, truck_roll_type, eero_type, priority in selected_combinations:
                req = TestCaseRequirement(
                    customer_type=customer_type,
                    scenario_type=scenario_type,
                    truck_roll_type=truck_roll_type,
                    count_needed=1,
                    priority=priority
                )
                req.eero_type = eero_type
                requirements.append(req)
                print(f"    {customer_type} {scenario_type} {eero_type} - {truck_roll_type} truck ({priority})")
        else:
            # Distribute count across base combinations
            base_count = count // len(base_combinations)
            remainder = count % len(base_combinations)
            
            for i, (customer_type, scenario_type, truck_roll_type, eero_type, priority) in enumerate(base_combinations):
                test_count = base_count + (1 if i < remainder else 0)
                if test_count > 0:
                    req = TestCaseRequirement(
                        customer_type=customer_type,
                        scenario_type=scenario_type,
                        truck_roll_type=truck_roll_type,
                        count_needed=test_count,
                        priority=priority
                    )
                    req.eero_type = eero_type
                    requirements.append(req)
                    print(f"    {customer_type} {scenario_type} {eero_type} - {truck_roll_type} truck ({priority}) x{test_count}")
        
        print(f"    Created {len(requirements)} requirement types for {sum(req.count_needed for req in requirements)} total test cases")
        return requirements
    
    def _check_requirement_diversity(self, requirements: List[TestCaseRequirement]) -> dict:
        """Check diversity of generated requirements"""
        diversity = {
            "customer_types": set(),
            "scenario_types": set(),
            "truck_roll_types": set(),
            "eero_types": set(),
            "unique_combinations": len(requirements)
        }
        
        for req in requirements:
            diversity["customer_types"].add(req.customer_type)
            diversity["scenario_types"].add(req.scenario_type)
            diversity["truck_roll_types"].add(req.truck_roll_type)
            diversity["eero_types"].add(getattr(req, 'eero_type', 'eero'))
        
        return {
            "customer_variety": len(diversity["customer_types"]),
            "scenario_variety": len(diversity["scenario_types"]),
            "truck_variety": len(diversity["truck_roll_types"]),
            "eero_variety": len(diversity["eero_types"]),
            "total_unique": diversity["unique_combinations"],
            "is_diverse": len(diversity["customer_types"]) > 1 or len(diversity["scenario_types"]) > 1
        }
    
    def _get_rag_context_for_coordination(self, user_story: str, additional_requirements: str) -> str:
        """Get comprehensive RAG context for coordination decisions"""
        if not self.rag_context:
            return "No specific business context available for coordination."
        
        context_text = "## BUSINESS INTELLIGENCE FOR COORDINATION:\n\n"
        
        try:
            # Get story-specific business contexts
            story_keywords = [word.lower() for word in user_story.split() 
                            if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that', 'this', 'from']]
            
            relevant_contexts = []
            for keyword in story_keywords[:8]:  # More keywords for better context
                contexts = self.rag_context.search_context(keyword)
                relevant_contexts.extend(contexts[:2])
            
            if relevant_contexts:
                context_text += "**Business Objectives and Validation Requirements:**\n"
                unique_contexts = {ctx.get('file_name', f'context_{i}'): ctx for i, ctx in enumerate(relevant_contexts[:5])}
                
                for ctx in unique_contexts.values():
                    purpose = ctx.get('business_purpose', 'Standard validation')
                    category = ctx.get('test_category', 'general')
                    segment = ctx.get('customer_segment', 'mixed')
                    keywords = ctx.get('keywords', [])
                    
                    context_text += f"- Purpose: {purpose}\n"
                    context_text += f"- Category: {category} | Segment: {segment}\n"
                    context_text += f"- Key Focus: {', '.join(keywords[:5])}\n\n"
            
            # Get all available categories and segments for coverage planning
            available_categories = self.rag_context.get_all_categories()
            available_segments = self.rag_context.get_all_customer_segments()
            
            context_text += f"**Available Test Categories:** {', '.join(available_categories)}\n"
            context_text += f"**Available Customer Segments:** {', '.join(available_segments)}\n\n"
            
            # Add requirements analysis
            if additional_requirements:
                req_keywords = [word.lower() for word in additional_requirements.split() 
                              if len(word) > 3]
                context_text += f"**Additional Requirements Focus:** {', '.join(req_keywords[:5])}\n"
            
            context_text += "\n**Coordination Guidance:**\n"
            context_text += "- Prioritize combinations that match business purposes above\n"
            context_text += "- Ensure coverage of relevant test categories\n"
            context_text += "- Balance customer segments based on business context\n"
            context_text += "- Include validation patterns mentioned in contexts\n"
            
        except Exception as e:
            context_text += f"Standard coordination approach required. (RAG error: {e})\n"
        
        return context_text
    
    def _get_combination_analysis_from_rag(self, user_story: str) -> dict:
        """Get combination analysis using RAG intelligence"""
        analysis = {
            'detected_type': 'standard',
            'order_types': ['install'],
            'customer_segments': ['residential'],
            'eero_types': ['basic'],
            'truck_roll_types': ['with'],
            'specific_scenarios': [],
            'business_priority': 'medium'
        }
        
        if not self.rag_context:
            return analysis
        
        try:
            # Get combination intelligence from RAG
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            
            # Extract detected combination type
            detected_combination = combo_intel.get('detected_combination', 'base_eero')
            workflow_type = combo_intel.get('workflow_type', 'standard_install')
            
            analysis['detected_type'] = detected_combination
            analysis['workflow_pattern'] = workflow_type
            
            # Analyze story content for comprehensive understanding
            story_lower = user_story.lower()
            
            # Detect order types
            if any(word in story_lower for word in ['install', 'new customer', 'setup', 'first time']):
                if 'install' not in analysis['order_types']:
                    analysis['order_types'].append('install')
            if any(word in story_lower for word in ['change', 'modify', 'add', 'remove', 'existing', 'cos']):
                if 'cos' not in analysis['order_types']:
                    analysis['order_types'].append('cos')
            if any(word in story_lower for word in ['both', 'all', 'complete', 'comprehensive']):
                analysis['order_types'] = ['install', 'cos']
            
            # Detect customer segments
            analysis['customer_segments'] = []
            if any(word in story_lower for word in ['residential', 'home', 'resi']):
                analysis['customer_segments'].append('residential')
            if any(word in story_lower for word in ['business', 'commercial', 'busi']):
                analysis['customer_segments'].append('business')
            if not analysis['customer_segments'] or any(word in story_lower for word in ['both', 'all']):
                analysis['customer_segments'] = ['residential', 'business']
            
            # Detect eero types
            analysis['eero_types'] = []
            if any(word in story_lower for word in ['plus', 'premium', 'enhanced', 'security']):
                analysis['eero_types'].append('plus')
            if any(word in story_lower for word in ['additional', 'multiple', 'mesh', 'devices']):
                analysis['eero_types'].append('additional')
            if any(word in story_lower for word in ['basic', 'standard']) or not analysis['eero_types']:
                analysis['eero_types'].append('basic')
            
            # Detect truck roll preferences
            if any(phrase in story_lower for phrase in ['no truck', 'self install', 'without technician']):
                analysis['truck_roll_types'] = ['no']
            elif any(phrase in story_lower for phrase in ['truck roll', 'technician', 'installation visit']):
                analysis['truck_roll_types'] = ['with']
            else:
                analysis['truck_roll_types'] = ['with', 'no']
            
            # Detect specific scenarios - enhanced device removal detection
            if any(word in story_lower for word in ['remove', 'delete', 'cancel', 'removal', 'removing']):
                analysis['specific_scenarios'].append('removal')
                analysis['business_priority'] = 'high'  # Device removal scenarios are high priority
            if any(word in story_lower for word in ['upgrade', 'enhance']):
                analysis['specific_scenarios'].append('upgrade')
            if any(word in story_lower for word in ['association', 'device', 'account', 'binding', 'lifecycle']):
                analysis['specific_scenarios'].append('device_association')
            if any(word in story_lower for word in ['process', 'workflow', 'validation']):
                analysis['specific_scenarios'].append('process_validation')
            
            # Determine business priority based on story complexity and RAG context
            complexity_indicators = len(analysis['order_types']) + len(analysis['customer_segments']) + len(analysis['eero_types'])
            if complexity_indicators >= 6 or 'process' in story_lower or 'validation' in story_lower:
                analysis['business_priority'] = 'high'
            elif complexity_indicators >= 4 or any(word in story_lower for word in ['complete', 'comprehensive']):
                analysis['business_priority'] = 'medium'
            else:
                analysis['business_priority'] = 'low'
            
        except Exception as e:
            print(f"     Combination analysis error: {e}")
        
        return analysis
    
    def _format_combination_analysis(self, analysis: dict) -> str:
        """Format combination analysis for LLM prompt"""
        text = "## COMBINATION INTELLIGENCE ANALYSIS:\n\n"
        
        text += f"**Detected Pattern:** {analysis.get('detected_type', 'standard')}\n"
        text += f"**Workflow Type:** {analysis.get('workflow_pattern', 'standard')}\n"
        text += f"**Business Priority:** {analysis.get('business_priority', 'medium').upper()}\n\n"
        
        text += f"**Story Analysis Results:**\n"
        text += f"- Order Types Detected: {', '.join(analysis.get('order_types', ['install']))}\n"
        text += f"- Customer Segments: {', '.join(analysis.get('customer_segments', ['residential']))}\n"
        text += f"- Eero Types: {', '.join(analysis.get('eero_types', ['basic']))}\n"
        text += f"- Truck Roll Types: {', '.join(analysis.get('truck_roll_types', ['with']))}\n"
        
        specific_scenarios = analysis.get('specific_scenarios', [])
        if specific_scenarios:
            text += f"- Specific Scenarios: {', '.join(specific_scenarios)}\n"
        
        text += f"\n**Coordination Recommendations:**\n"
        text += f"- Focus on {analysis.get('business_priority', 'medium')} priority combinations\n"
        text += f"- Include {len(analysis.get('order_types', []))} order type(s)\n"
        text += f"- Cover {len(analysis.get('customer_segments', []))} segment(s)\n"
        text += f"- Support {len(analysis.get('eero_types', []))} eero type(s)\n"
        
        return text
    
    def _parse_enhanced_requirements(self, response_content: str, combination_analysis: dict) -> List[TestCaseRequirement]:
        """Parse LLM response with enhanced validation and metadata"""
        requirements = []
        lines = response_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if '|' in line and line.count('|') >= 4:
                try:
                    parts = line.split('|')
                    customer_type = parts[0].strip().upper()
                    scenario_type = parts[1].strip().lower()
                    truck_roll_type = parts[2].strip().title()
                    count = int(parts[3].strip())
                    business_priority = parts[4].strip().upper() if len(parts) > 4 else 'MEDIUM'
                    
                    # Validate parsed values
                    if (customer_type in ['RESI', 'BUSI'] and 
                        scenario_type in ['install', 'cos'] and 
                        truck_roll_type in ['No', 'With'] and 
                        count > 0 and
                        business_priority in ['HIGH', 'MEDIUM', 'LOW']):
                        
                        req = TestCaseRequirement(
                            customer_type=customer_type,
                            scenario_type=scenario_type,
                            truck_roll_type=truck_roll_type,
                            count_needed=count,
                            priority=business_priority.lower()
                        )
                        
                        requirements.append(req)
                        
                except (ValueError, IndexError):
                    continue
        
        return requirements
    
    def _enhance_requirements_with_rag(self, requirements: List[TestCaseRequirement], 
                                     combination_analysis: dict) -> List[TestCaseRequirement]:
        """Enhance requirements with RAG-derived metadata"""
        
        for req in requirements:
            # Add combination metadata based on analysis
            req.detected_combination = combination_analysis.get('detected_type', 'standard')
            req.workflow_pattern = combination_analysis.get('workflow_pattern', 'standard')
            req.business_priority_level = combination_analysis.get('business_priority', 'medium')
            
            # Determine eero type based on combination analysis and requirement
            eero_types = combination_analysis.get('eero_types', ['basic'])
            if 'plus' in eero_types:
                req.eero_type = 'eero_plus'
            elif 'additional' in eero_types:
                req.eero_type = 'eero_additional'
            else:
                req.eero_type = 'eero'
            
            # Service codes will be assigned by generation agent based on RESI/BUSI rules
            
            # Set customer status based on scenario
            req.customer_status = 'new' if req.scenario_type == 'install' else 'existing'
            
            # Add business context description
            segment_name = 'Residential' if req.customer_type == 'RESI' else 'Business'
            scenario_name = 'Install' if req.scenario_type == 'install' else 'Change of Service'
            truck_name = 'With Truck Roll' if req.truck_roll_type == 'With' else 'No Truck Roll'
            
            req.description = f"{scenario_name} {segment_name} {req.eero_type.replace('_', ' ').title()} - {truck_name}"
            
        return requirements
    
    def _create_intelligent_fallback(self, user_story: str, combination_analysis: dict, 
                                   count: int) -> List[TestCaseRequirement]:
        """Create intelligent fallback requirements using RAG analysis"""
        
        print(f" Creating intelligent fallback based on story analysis...")
        
        order_types = combination_analysis.get('order_types', ['install'])
        customer_segments = combination_analysis.get('customer_segments', ['residential'])
        eero_types = combination_analysis.get('eero_types', ['basic'])
        truck_roll_types = combination_analysis.get('truck_roll_types', ['with'])
        business_priority = combination_analysis.get('business_priority', 'medium')
        
        print(f"    Analysis: {len(order_types)} order types, {len(customer_segments)} segments, {len(eero_types)} eero types")
        
        requirements = []
        
        # Create balanced distribution based on analysis
        scenarios = []
        for order_type in order_types:
            for segment in customer_segments:
                customer_type = 'RESI' if segment == 'residential' else 'BUSI'
                for truck_type in truck_roll_types:
                    truck_roll = 'With' if truck_type == 'with' else 'No'
                    scenarios.append((customer_type, order_type, truck_roll))
        
        # Distribute count across scenarios
        if len(scenarios) <= count:
            # We have fewer or equal scenarios than needed count
            base_count = count // len(scenarios)
            remainder = count % len(scenarios)
            
            for i, (customer_type, scenario_type, truck_roll_type) in enumerate(scenarios):
                req_count = base_count + (1 if i < remainder else 0)
                if req_count > 0:
                    req = TestCaseRequirement(
                        customer_type=customer_type,
                        scenario_type=scenario_type,
                        truck_roll_type=truck_roll_type,
                        count_needed=req_count,
                        priority=business_priority
                    )
                    requirements.append(req)
        else:
            # We have more scenarios than count, select best ones
            priority_scenarios = scenarios[:count]
            for customer_type, scenario_type, truck_roll_type in priority_scenarios:
                req = TestCaseRequirement(
                    customer_type=customer_type,
                    scenario_type=scenario_type,
                    truck_roll_type=truck_roll_type,
                    count_needed=1,
                    priority=business_priority
                )
                requirements.append(req)
        
        # Enhance with RAG metadata
        requirements = self._enhance_requirements_with_rag(requirements, combination_analysis)
        
        print(f"    Created {len(requirements)} intelligent fallback requirements")
        return requirements
    
    def _adjust_requirements_count(self, requirements: List[TestCaseRequirement], 
                                 target_count: int) -> List[TestCaseRequirement]:
        """Adjust requirements to match target count intelligently"""
        
        current_total = sum(req.count_needed for req in requirements)
        
        if current_total == target_count:
            return requirements
        elif current_total < target_count:
            # Need to add more - distribute to high priority first
            deficit = target_count - current_total
            high_priority_reqs = [req for req in requirements if req.priority == 'high']
            
            if high_priority_reqs:
                per_req = deficit // len(high_priority_reqs)
                remainder = deficit % len(high_priority_reqs)
                
                for i, req in enumerate(high_priority_reqs):
                    req.count_needed += per_req + (1 if i < remainder else 0)
            else:
                # Distribute to all requirements
                per_req = deficit // len(requirements)
                remainder = deficit % len(requirements)
                
                for i, req in enumerate(requirements):
                    req.count_needed += per_req + (1 if i < remainder else 0)
        else:
            # Need to reduce - reduce from low priority first
            excess = current_total - target_count
            low_priority_reqs = [req for req in requirements if req.priority == 'low']
            
            if low_priority_reqs:
                for req in low_priority_reqs:
                    if excess <= 0:
                        break
                    if req.count_needed > 1:
                        reduction = min(excess, req.count_needed - 1)
                        req.count_needed -= reduction
                        excess -= reduction
            
            # If still excess, reduce from others
            if excess > 0:
                for req in requirements:
                    if excess <= 0:
                        break
                    if req.count_needed > 1:
                        reduction = min(excess, req.count_needed - 1)
                        req.count_needed -= reduction
                        excess -= reduction
        
        return requirements
