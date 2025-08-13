from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCaseRequirement

class CoordinatorAgent:
    """Enhanced Coordinator Agent with step preservation emphasis"""
    
    def __init__(self, llm: AzureChatOpenAI, rag_context=None):
        self.llm = llm
        self.rag_context = rag_context
        
        # Enhanced coordination prompt with step preservation focus
        self.coordination_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the EXPERT COORDINATOR AGENT with deep understanding of COMPLETE EERO WORKFLOWS and step preservation requirements.

## COMPLETE WORKFLOW UNDERSTANDING ##

**FULL EERO TEST CASE WORKFLOW (10+ STEPS REQUIRED):**
1. **Prerequisites**: Customer and device setup
2. **ACSR Search**: Customer lookup and verification  
3. **Order Workflow**: Change of Service or Install initiation
4. **Service Configuration**: Adding eero service with correct codes
5. **Order Completion**: Status updates and finalization ✅ CRITICAL
6. **Kafka Validation**: Message queue verification ✅ CRITICAL
7. **Banhammer Portal**: Device configuration checks ✅ CRITICAL  
8. **API Testing**: eero-provisioning endpoint validation ✅ CRITICAL
9. **eero Insight Setup**: Network creation and management ✅ CRITICAL
10. **Final Verification**: Complete workflow validation ✅ CRITICAL

## STEP PRESERVATION MANDATE ##

**CRITICAL REQUIREMENT:**
- Generated test cases MUST include ALL steps from template
- Each requirement should target templates with COMPLETE workflows
- Prefer comprehensive templates with 10+ steps including validation
- Ensure templates contain Kafka, API, and eero Insight verification steps

## COMPREHENSIVE COVERAGE STRATEGY ##

**SCENARIO DISTRIBUTION PRIORITIES:**
1. **Complete Workflow Coverage**: Both install AND CoS with full verification
2. **End-to-End Validation**: All templates must include complete validation chains
3. **Quality Over Quantity**: Prefer fewer comprehensive test cases over many partial ones
4. **Critical Step Coverage**: Ensure all generated test cases include validation steps

**TEMPLATE QUALITY REQUIREMENTS:**
- Templates must contain complete order-to-verification workflow
- Must include Kafka queue validation steps
- Must include API endpoint testing steps  
- Must include eero Insight setup and verification
- Must include final validation and confirmation steps"""),
            
            ("human", """## COMPREHENSIVE WORKFLOW ANALYSIS ##

**USER STORY:** {user_story}
**ADDITIONAL REQUIREMENTS:** {additional_requirements}
**REQUESTED TEST CASES:** {number_of_test_cases}
**BUSINESS CONTEXT:** {rag_context}

## COMPLETE WORKFLOW ANALYSIS ##

**STEP 1: WORKFLOW SCOPE ANALYSIS**
Analyze the user story for complete workflow requirements:

🔍 **Process Completeness Questions:**
- Does this require complete order-to-verification workflow?
- Should this include Kafka queue validation steps?
- Should this include API endpoint testing?
- Should this include eero Insight setup verification?
- Does this need end-to-end validation coverage?

**STEP 2: COMPREHENSIVE SCENARIO PLANNING**

📋 **Complete Install Workflow Requirements:**
- New customer account creation + device association
- Order processing + status completion
- Kafka queue validation + message verification  
- API endpoint testing + response validation
- eero Insight network creation + customer setup
- Final verification + complete workflow validation

📋 **Complete CoS Workflow Requirements:**
- Existing customer service modification + device updates
- Order processing + status completion
- Kafka queue validation + service change verification
- API endpoint testing + updated response validation  
- eero Insight configuration updates + service verification
- Final verification + complete modification validation

**STEP 3: QUALITY-FOCUSED DISTRIBUTION**

🎯 **Template Quality Requirements:**
- Each test case must use templates with 10+ comprehensive steps
- Must include complete validation chains (Kafka + API + Insight)
- Must cover end-to-end workflow from order to final verification
- Must include combination-specific validation steps

🎯 **Comprehensive Coverage Strategy:**
For {number_of_test_cases} test cases, prioritize:
- **Complete Workflows**: Each test case must be comprehensive
- **Quality Templates**: Use only templates with full validation chains
- **End-to-End Coverage**: Order creation through final verification
- **Balanced Distribution**: Mix of install/CoS with complete workflows

**STEP 4: COMPLETE WORKFLOW REQUIREMENTS**

Generate requirements ensuring COMPLETE workflow coverage:

**MANDATORY REQUIREMENTS:**
✅ Each requirement must target templates with complete workflows
✅ Must include both install AND CoS scenarios (unless explicitly single-type)
✅ Must ensure templates contain Kafka validation steps
✅ Must ensure templates contain API testing steps
✅ Must ensure templates contain eero Insight verification
✅ Must prioritize comprehensive end-to-end coverage

**DISTRIBUTION FORMAT:**
CUSTOMER_TYPE|SCENARIO_TYPE|TRUCK_ROLL_TYPE|COUNT

**QUALITY EMPHASIS:**
- Prefer comprehensive templates with complete validation
- Ensure each generated test case covers full workflow
- Target templates with proven complete step coverage
- Balance customer types while maintaining workflow completeness

**CRITICAL INSTRUCTIONS:**
- Unless explicitly stated otherwise, plan for BOTH install AND CoS scenarios
- Prioritize comprehensive workflow coverage over simple test quantity
- Ensure all requirements target templates with complete validation chains
- Focus on quality comprehensive test cases with 10+ steps each

Generate the comprehensive workflow requirements:""")
        ])
    
    async def analyze_requirements(self, user_story: str, additional_requirements: str, 
                                 number_of_test_cases: int) -> List[TestCaseRequirement]:
        """Enhanced requirement analysis with step preservation focus"""
        
        # Get combination and workflow analysis
        combination_intel = self._analyze_complete_workflows(user_story, additional_requirements)
        rag_context = self._get_business_context(user_story, additional_requirements)
        
        print(f"   🎯 Workflow analysis: {combination_intel['workflow_completeness']}")
        print(f"   📊 Quality focus: {combination_intel['quality_requirements']}")
        
        try:
            chain = self.coordination_prompt | self.llm
            response = await chain.ainvoke({
                'user_story': user_story,
                'additional_requirements': additional_requirements,
                'number_of_test_cases': number_of_test_cases,
                'rag_context': rag_context
            })
            
            # Parse response with quality focus
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
                print("⚠️  No valid requirements parsed, using comprehensive fallback")
                return self._create_comprehensive_fallback(user_story, number_of_test_cases)
            
            # Adjust count and ensure quality focus
            total_count = sum(req.count_needed for req in requirements)
            if total_count != number_of_test_cases:
                requirements = self._adjust_requirements_count(requirements, number_of_test_cases)
            
            # Ensure comprehensive coverage
            requirements = self._ensure_comprehensive_coverage(requirements, combination_intel)
            
            print(f"   ✅ Generated {len(requirements)} comprehensive requirements")
            return requirements
            
        except Exception as e:
            print(f"⚠️  Enhanced coordination failed: {e}, using comprehensive fallback")
            return self._create_comprehensive_fallback(user_story, number_of_test_cases)
    
    def _analyze_complete_workflows(self, user_story: str, additional_requirements: str) -> dict:
        """Analyze requirements for complete workflow coverage"""
        
        story_text = f"{user_story} {additional_requirements}".lower()
        
        # Workflow completeness analysis
        workflow_completeness = "full"  # Default to full workflows
        quality_requirements = ["complete_validation"]
        
        # Check for process-related keywords that require complete workflows
        if any(keyword in story_text for keyword in [
            'process', 'workflow', 'association', 'end-to-end', 'complete', 'validation'
        ]):
            workflow_completeness = "comprehensive"
            quality_requirements.extend(["kafka_validation", "api_testing", "insight_setup"])
        
        # Check for validation-specific requirements
        if any(keyword in story_text for keyword in [
            'verify', 'validate', 'test', 'ensure', 'confirm'
        ]):
            quality_requirements.extend(["verification_steps", "response_validation"])
        
        # Determine scenario requirements with quality focus
        needs_install = True
        needs_cos = True
        
        # Only exclude scenarios if explicitly stated
        if any(phrase in story_text for phrase in ['only existing', 'existing customers only']):
            needs_install = False
        if any(phrase in story_text for phrase in ['only new', 'new customers only']):
            needs_cos = False
        
        # Force comprehensive coverage for process stories
        if any(keyword in story_text for keyword in ['process', 'workflow', 'association']):
            needs_install = True
            needs_cos = True
            workflow_completeness = "comprehensive"
        
        return {
            'workflow_completeness': workflow_completeness,
            'quality_requirements': quality_requirements,
            'needs_install': needs_install,
            'needs_cos': needs_cos,
            'comprehensive_validation_required': True
        }
    
    def _create_comprehensive_fallback(self, user_story: str, count: int) -> List[TestCaseRequirement]:
        """Create comprehensive fallback with complete workflow focus"""
        
        print(f"🔧 Creating comprehensive workflow fallback for {count} test cases...")
        
        # Analyze for comprehensive requirements
        workflow_analysis = self._analyze_complete_workflows(user_story, "")
        
        needs_install = workflow_analysis['needs_install']
        needs_cos = workflow_analysis['needs_cos']
        
        print(f"   📊 Comprehensive analysis: Install={needs_install}, CoS={needs_cos}")
        print(f"   🎯 Quality focus: Complete workflows with full validation")
        
        # Build scenarios with quality focus
        scenarios = []
        customers = ['RESI', 'BUSI']
        truck_types = ['No', 'With']
        
        if needs_install:
            scenarios.append('install')
        if needs_cos:
            scenarios.append('cos')
        
        # Default to both if none specified
        if not scenarios:
            scenarios = ['install', 'cos']
            print("   🔄 Defaulting to comprehensive BOTH install and CoS coverage")
        
        # Distribute with quality focus (prefer fewer comprehensive test cases)
        requirements = []
        
        # For comprehensive coverage, distribute evenly but prioritize quality
        if count <= 4:
            # Small count - ensure both scenarios covered
            if len(scenarios) == 2:  # Both install and CoS
                # 2 install, 2 CoS
                requirements.extend([
                    TestCaseRequirement("RESI", "install", "No", 1, "high"),
                    TestCaseRequirement("RESI", "cos", "No", 1, "high"),
                    TestCaseRequirement("BUSI", "install", "No", 1, "high"),
                    TestCaseRequirement("BUSI", "cos", "No", 1, "high")
                ])
            else:
                # Single scenario type
                scenario = scenarios[0]
                requirements.extend([
                    TestCaseRequirement("RESI", scenario, "No", 2, "high"),
                    TestCaseRequirement("BUSI", scenario, "No", 2, "high")
                ])
        
        elif count <= 8:
            # Medium count - comprehensive coverage with truck roll variety
            for scenario in scenarios:
                for customer in customers:
                    for truck in truck_types:
                        if len(requirements) < count:
                            requirements.append(TestCaseRequirement(
                                customer, scenario, truck, 1, "high"
                            ))
        
        else:
            # Large count - full comprehensive coverage
            base_per_combo = max(1, count // (len(scenarios) * len(customers) * len(truck_types)))
            remaining = count
            
            for scenario in scenarios:
                for customer in customers:
                    for truck in truck_types:
                        if remaining > 0:
                            use_count = min(base_per_combo, remaining)
                            requirements.append(TestCaseRequirement(
                                customer, scenario, truck, use_count, "high"
                            ))
                            remaining -= use_count
                            print(f"   ✅ {customer} {scenario} - {truck} truck (x{use_count})")
        
        # Adjust to exact count
        current_total = sum(req.count_needed for req in requirements)
        if current_total != count:
            diff = count - current_total
            if diff > 0 and requirements:
                requirements[0].count_needed += diff
                print(f"   📈 Added {diff} extra for exact count")
            elif diff < 0:
                # Reduce from largest requirement
                for req in sorted(requirements, key=lambda r: r.count_needed, reverse=True):
                    if req.count_needed > 1 and diff < 0:
                        reduction = min(req.count_needed - 1, abs(diff))
                        req.count_needed -= reduction
                        diff += reduction
                        if diff >= 0:
                            break
        
        print(f"   ✅ Created {len(requirements)} comprehensive requirements")
        return requirements
    
    def _ensure_comprehensive_coverage(self, requirements: List[TestCaseRequirement], 
                                     workflow_analysis: dict) -> List[TestCaseRequirement]:
        """Ensure requirements target comprehensive workflows"""
        
        # Add quality markers to requirements
        for req in requirements:
            req.priority = "high"  # All requirements should be high quality
            
            # Add workflow completeness requirement
            if not hasattr(req, 'workflow_requirements'):
                req.workflow_requirements = workflow_analysis['quality_requirements']
        
        # Ensure both scenarios are represented if needed
        scenario_types = set(req.scenario_type for req in requirements)
        
        if (workflow_analysis['needs_install'] and workflow_analysis['needs_cos'] and 
            len(scenario_types) == 1):
            
            print(f"   🔄 Adding missing scenario type for comprehensive coverage")
            
            # Convert one requirement to the missing scenario
            current_scenario = list(scenario_types)[0]
            missing_scenario = 'cos' if current_scenario == 'install' else 'install'
            
            # Find requirement to split
            largest_req = max(requirements, key=lambda r: r.count_needed)
            if largest_req.count_needed > 1:
                largest_req.count_needed -= 1
                
                # Add missing scenario requirement
                new_req = TestCaseRequirement(
                    customer_type=largest_req.customer_type,
                    scenario_type=missing_scenario,
                    truck_roll_type=largest_req.truck_roll_type,
                    count_needed=1,
                    priority="high"
                )
                requirements.append(new_req)
                print(f"   ✅ Added {missing_scenario} scenario for balanced coverage")
        
        return requirements
    
    def _get_business_context(self, user_story: str, additional_requirements: str) -> str:
        """Get comprehensive business context for workflow planning"""
        
        if not self.rag_context:
            return "Comprehensive workflow validation required - complete end-to-end testing."
        
        # Search for comprehensive workflow contexts
        story_text = f"{user_story} {additional_requirements}".lower()
        
        # Enhanced search terms for comprehensive workflows
        search_terms = [
            'eero', 'association', 'process', 'workflow', 'validation', 
            'kafka', 'api', 'insight', 'complete', 'end-to-end'
        ]
        
        # Add story-specific terms
        story_terms = [word for word in story_text.split() 
                      if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'that']]
        search_terms.extend(story_terms[:5])
        
        # Search for relevant contexts
        relevant_contexts = []
        for term in search_terms:
            try:
                contexts = self.rag_context.search_context(term)
                relevant_contexts.extend(contexts[:2])
            except:
                continue
        
        if not relevant_contexts:
            return "Standard comprehensive workflow testing with complete validation chain."
        
        # Format comprehensive context
        context_text = "## COMPREHENSIVE WORKFLOW CONTEXT:\n\n"
        context_text += "**Quality Focus**: Complete end-to-end workflow validation\n"
        context_text += "**Step Requirements**: 10+ comprehensive steps including validation\n\n"
        
        unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in relevant_contexts}
        
        for i, (filename, ctx) in enumerate(list(unique_contexts.items())[:3], 1):
            context_text += f"**Workflow Context {i}**:\n"
            context_text += f"- **Purpose**: {ctx.get('business_purpose', 'N/A')}\n"
            context_text += f"- **Category**: {ctx.get('test_category', 'N/A')}\n"
            context_text += f"- **Keywords**: {', '.join(ctx.get('keywords', []))}\n"
            context_text += f"- **Quality Level**: Comprehensive validation required\n\n"
        
        return context_text
    
    def _adjust_requirements_count(self, requirements: List[TestCaseRequirement], 
                                 target_count: int) -> List[TestCaseRequirement]:
        """Adjust requirements to match target count while maintaining quality"""
        
        current_total = sum(req.count_needed for req in requirements)
        
        if current_total == target_count:
            return requirements
        elif current_total < target_count:
            # Need to add more - distribute evenly
            deficit = target_count - current_total
            per_req = deficit // len(requirements)
            remaining = deficit % len(requirements)
            
            for req in requirements:
                req.count_needed += per_req
                if remaining > 0:
                    req.count_needed += 1
                    remaining -= 1
        else:
            # Need to reduce - reduce from largest first
            excess = current_total - target_count
            requirements_sorted = sorted(requirements, key=lambda r: r.count_needed, reverse=True)
            
            for req in requirements_sorted:
                if excess <= 0:
                    break
                if req.count_needed > 1:
                    reduction = min(excess, req.count_needed - 1)
                    req.count_needed -= reduction
                    excess -= reduction
        
        return requirements