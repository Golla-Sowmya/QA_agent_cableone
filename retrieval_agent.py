from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class RetrievalAgent:
    """Enhanced Retrieval Agent prioritizing complete workflow templates"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        
        # Enhanced selection prompt with complete workflow focus
        self.selection_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the EXPERT RETRIEVAL AGENT with focus on COMPLETE WORKFLOW TEMPLATES that preserve all critical steps.

## COMPLETE WORKFLOW TEMPLATE REQUIREMENTS ##

**MANDATORY TEMPLATE CHARACTERISTICS:**
1. **Complete Step Coverage**: Templates must contain 10+ comprehensive steps
2. **End-to-End Workflow**: From order creation to final verification
3. **Critical Validation Steps**: Must include ALL of these:
   - Order completion and status updates
   - Kafka queue validation and message verification
   - Banhammer portal device configuration checks
   - API endpoint testing and response validation
   - eero Insight network setup and verification
   - Final API verification and workflow completion

**TEMPLATE QUALITY ASSESSMENT:**
- **EXCELLENT (90-100 points)**: 10+ steps with complete validation chain
- **GOOD (70-89 points)**: 8-9 steps with most validation steps
- **FAIR (50-69 points)**: 6-7 steps with some validation
- **POOR (<50 points)**: Incomplete workflows, missing critical validation

## CRITICAL STEP VERIFICATION ##

**Templates MUST contain evidence of:**
✅ **Kafka Validation**: "kafka", "eero-order queue", "billing-system"
✅ **API Testing**: "eero-provisioning", "swagger", "endpoint"
✅ **Banhammer Portal**: "banhammer", "mac address", "ldap"
✅ **eero Insight**: "eero insight", "network creation", "fleet summary"
✅ **Complete Verification**: "final", "response", "validation"

## INTELLIGENT SELECTION STRATEGY ##

**SELECTION PRIORITY ORDER:**
1. **Complete Workflow Match**: Exact customer/scenario/truck + complete validation
2. **Quality Template**: High step count + comprehensive validation chain
3. **Combination Relevance**: Matches eero product combination requirements
4. **Template Completeness**: Proven end-to-end workflow coverage

**DIVERSITY WITH QUALITY:**
- When selecting multiple templates, choose different combinations
- BUT maintain quality requirement - all must be comprehensive
- Prefer templates with 10+ steps and complete validation chains
- Avoid partial or incomplete workflow templates"""),
            
            ("human", """## COMPLETE WORKFLOW TEMPLATE SELECTION ##

**SELECTION TARGET:**
- Customer Type: {customer_type}
- Scenario Type: {scenario_type}
- Truck Roll: {truck_roll_type}
- Count Needed: {count_needed}

**USER STORY CONTEXT:**
{user_story_context}

**QUALITY REQUIREMENTS:**
{rag_context}

**AVAILABLE MATCHING TEMPLATES:**
{available_cases}

## COMPREHENSIVE TEMPLATE ANALYSIS ##

**STEP 1: WORKFLOW COMPLETENESS ASSESSMENT**
For each available template, assess:
- **Step Count**: Does it have 10+ comprehensive steps?
- **Critical Validation**: Does it include Kafka + API + Insight validation?
- **End-to-End Coverage**: Does it cover complete order-to-verification workflow?
- **Quality Indicators**: Evidence of comprehensive testing approach?

**STEP 2: TEMPLATE QUALITY SCORING**
Rate each template on:
1. **Completeness (40 points)**: Complete workflow with all validation steps
2. **Step Richness (30 points)**: High step count with detailed instructions
3. **Validation Coverage (20 points)**: Includes all critical validation steps
4. **Combination Relevance (10 points)**: Matches eero product requirements

**STEP 3: QUALITY-FIRST SELECTION**
Select templates based on:
✅ **FIRST PRIORITY**: Complete workflow templates (10+ steps)
✅ **SECOND PRIORITY**: Templates with critical validation steps
✅ **THIRD PRIORITY**: Combination-specific relevance
✅ **FOURTH PRIORITY**: Diversity when selecting multiple

**CRITICAL SELECTION RULES:**
- NEVER select partial or incomplete workflow templates
- ALWAYS prioritize templates with complete validation chains
- ONLY select templates that contain Kafka, API, and Insight validation
- When selecting multiple, maintain quality while adding diversity

**TEMPLATE QUALITY VERIFICATION:**
Before selecting, ensure each template contains:
- Order creation and completion steps
- Kafka queue validation steps
- API endpoint testing steps  
- eero Insight setup and verification steps
- Final validation and confirmation steps

**OUTPUT FORMAT:**
Respond with ONLY the selected test case IDs of COMPLETE WORKFLOW templates:
TC_ID_1
TC_ID_2
TC_ID_3

**MANDATORY REQUIREMENT:**
Only select templates that provide COMPLETE end-to-end workflow coverage with comprehensive validation steps.

Selected complete workflow template IDs:""")
        ])
    
    async def find_test_cases(self, requirement: TestCaseRequirement, 
                            user_story: str) -> List[TestCase]:
        """Enhanced retrieval focusing on complete workflow templates"""
        
        print(f"   🔍 Searching for COMPLETE workflow templates...")
        
        # Find exact basic matches
        matching_cases = [
            tc for tc in self.test_cases
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated)
        ]
        
        if not matching_cases:
            print(f"   ❌ No exact matches found")
            return []
        
        # Enhanced scoring with workflow completeness focus
        complete_workflow_cases = self._score_workflow_completeness(
            matching_cases, requirement, user_story
        )
        
        print(f"   🔍 Found {len(matching_cases)} matches, analyzing workflow completeness...")
        
        # Filter for quality templates only
        quality_templates = [
            (score, tc) for score, tc in complete_workflow_cases 
            if score >= 70  # Only select good quality templates
        ]
        
        if not quality_templates:
            print(f"   ⚠️  No high-quality complete workflow templates found")
            # Fallback to best available, but with warning
            quality_templates = complete_workflow_cases[:requirement.count_needed]
            print(f"   🔄 Using best available templates (may be incomplete)")
        
        print(f"   ✅ Found {len(quality_templates)} high-quality complete workflow templates")
        
        if len(quality_templates) <= requirement.count_needed:
            selected = [tc for _, tc in quality_templates]
            print(f"   ✅ Selected all {len(selected)} complete workflow templates")
            return selected
        
        # Use LLM for intelligent selection among quality templates
        print(f"   🧠 Using LLM for optimal selection of {requirement.count_needed} from {len(quality_templates)} quality templates")
        
        try:
            # Enhanced RAG context for quality focus
            rag_context = self._get_quality_focused_context(requirement, user_story)
            
            # Format quality templates for selection
            available_text = ""
            for score, tc in quality_templates:
                workflow_assessment = self._assess_workflow_completeness(tc)
                
                available_text += f"{tc.id} (Quality Score: {score}/100)\n"
                available_text += f"Title: {tc.title}\n"
                available_text += f"Steps: {len(tc.steps)}\n"
                available_text += f"Workflow Assessment: {workflow_assessment}\n"
                available_text += f"Content preview: {tc.content[:300]}...\n"
                available_text += "-" * 60 + "\n\n"
            
            chain = self.selection_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type,
                'truck_roll_type': requirement.truck_roll_type,
                'count_needed': requirement.count_needed,
                'user_story_context': user_story[:600],
                'rag_context': rag_context,
                'available_cases': available_text[:4000]
            })
            
            # Parse selected IDs
            selected_ids = [line.strip() for line in response.content.strip().split('\n') 
                          if line.strip() and line.strip().startswith('TC_')]
            
            # Find selected test cases
            selected_cases = []
            for tc_id in selected_ids:
                for score, tc in quality_templates:
                    if tc.id == tc_id and tc not in selected_cases:
                        selected_cases.append(tc)
                        workflow_assessment = self._assess_workflow_completeness(tc)
                        print(f"     📝 Selected: {tc.id} (Score: {score}, Workflow: {workflow_assessment})")
                        break
            
            if len(selected_cases) >= requirement.count_needed:
                result = selected_cases[:requirement.count_needed]
                print(f"   ✅ LLM selected {len(result)} optimal complete workflow templates")
                return result
            else:
                # Fallback to top quality templates
                result = [tc for _, tc in quality_templates[:requirement.count_needed]]
                print(f"   ✅ Using top {len(result)} quality templates (LLM fallback)")
                return result
                
        except Exception as e:
            print(f"   ⚠️  Enhanced selection failed: {e}, using top quality templates")
            result = [tc for _, tc in quality_templates[:requirement.count_needed]]
            return result
    
    def _score_workflow_completeness(self, test_cases: List[TestCase], 
                                   requirement: TestCaseRequirement, 
                                   user_story: str) -> List[tuple]:
        """Score test cases based on workflow completeness"""
        
        scored_cases = []
        
        for tc in test_cases:
            score = 0
            content_lower = tc.content.lower()
            
            # Step count scoring (30 points)
            step_count = len(tc.steps)
            if step_count >= 10:
                score += 30
            elif step_count >= 8:
                score += 25
            elif step_count >= 6:
                score += 20
            elif step_count >= 4:
                score += 15
            else:
                score += 10
            
            # Critical workflow step verification (50 points total)
            critical_steps = {
                'kafka_validation': any(keyword in content_lower for keyword in 
                                      ['kafka', 'eero-order queue', 'billing-system']),
                'api_testing': any(keyword in content_lower for keyword in 
                                 ['eero-provisioning', 'swagger', 'endpoint', 'api']),
                'banhammer_portal': any(keyword in content_lower for keyword in 
                                      ['banhammer', 'mac address', 'ldap']),
                'eero_insight': any(keyword in content_lower for keyword in 
                                  ['eero insight', 'network', 'fleet summary', 'insight']),
                'final_verification': any(keyword in content_lower for keyword in 
                                        ['final', 'response', 'validation', 'verify'])
            }
            
            critical_score = sum(10 for step_present in critical_steps.values() if step_present)
            score += critical_score
            
            # Content depth scoring (10 points)
            if len(tc.content) > 4000:
                score += 10
            elif len(tc.content) > 2000:
                score += 7
            elif len(tc.content) > 1000:
                score += 5
            else:
                score += 2
            
            # Quality indicators (10 points)
            quality_indicators = [
                'prerequisites', 'expected result', 'verification', 
                'validate', 'confirm', 'ensure'
            ]
            quality_score = min(10, sum(2 for indicator in quality_indicators 
                                      if indicator in content_lower))
            score += quality_score
            
            scored_cases.append((score, tc))
        
        # Sort by score (highest first)
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        # Log scoring results
        print(f"   📊 Workflow completeness scoring:")
        for score, tc in scored_cases[:3]:
            workflow_quality = "EXCELLENT" if score >= 90 else "GOOD" if score >= 70 else "FAIR" if score >= 50 else "POOR"
            print(f"     {tc.id}: {score}/100 ({workflow_quality})")
        
        return scored_cases
    
    def _assess_workflow_completeness(self, tc: TestCase) -> str:
        """Assess the completeness of a workflow template"""
        
        content_lower = tc.content.lower()
        step_count = len(tc.steps)
        
        # Check for critical components
        has_kafka = any(keyword in content_lower for keyword in ['kafka', 'queue'])
        has_api = any(keyword in content_lower for keyword in ['api', 'endpoint', 'swagger'])
        has_insight = any(keyword in content_lower for keyword in ['insight', 'network'])
        has_banhammer = any(keyword in content_lower for keyword in ['banhammer', 'ldap'])
        
        critical_components = sum([has_kafka, has_api, has_insight, has_banhammer])
        
        if step_count >= 10 and critical_components >= 3:
            return "COMPLETE (Full workflow with validation)"
        elif step_count >= 8 and critical_components >= 2:
            return "GOOD (Most workflow steps present)"
        elif step_count >= 6 and critical_components >= 1:
            return "PARTIAL (Some workflow steps missing)"
        else:
            return "INCOMPLETE (Missing critical workflow steps)"
    
    def _get_quality_focused_context(self, requirement: TestCaseRequirement, 
                                   user_story: str) -> str:
        """Get RAG context focused on quality and completeness"""
        
        context_text = "## QUALITY-FOCUSED TEMPLATE SELECTION CONTEXT:\n\n"
        context_text += "**Primary Requirement**: Complete end-to-end workflow templates\n"
        context_text += "**Quality Standards**: 10+ steps with comprehensive validation\n"
        context_text += "**Critical Components**: Kafka + API + Insight + Banhammer validation\n\n"
        
        # Get standard RAG context
        if self.rag_context:
            # Search for quality-related contexts
            segment = 'residential' if requirement.customer_type == 'RESI' else 'business'
            category = 'install' if requirement.scenario_type == 'install' else 'change_of_service'
            
            segment_contexts = self.rag_context.get_context_by_customer_segment(segment)
            category_contexts = self.rag_context.get_context_by_category(category)
            
            all_contexts = segment_contexts + category_contexts
            unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in all_contexts}
            
            for i, (filename, ctx) in enumerate(list(unique_contexts.items())[:2], 1):
                context_text += f"**Quality Context {i}**:\n"
                context_text += f"- **Purpose**: {ctx.get('business_purpose', 'N/A')}\n"
                context_text += f"- **Expected Quality**: Complete workflow validation\n"
                context_text += f"- **Requirements**: End-to-end testing with all verification steps\n\n"
        
        context_text += "**SELECTION MANDATE**: Only select templates with proven complete workflows\n"
        
        return context_text
    
    def get_available_test_case_types(self) -> dict:
        """Get breakdown with quality assessment"""
        breakdown = {}
        quality_breakdown = {}
        
        for tc in self.test_cases:
            if not tc.is_generated:
                key = f"{tc.customer_type}-{tc.scenario_type}-{tc.truck_roll_type}Truck"
                breakdown[key] = breakdown.get(key, 0) + 1
                
                # Assess quality
                workflow_quality = self._assess_workflow_completeness(tc)
                quality_key = f"{key}-{workflow_quality}"
                quality_breakdown[quality_key] = quality_breakdown.get(quality_key, 0) + 1
        
        return {
            'basic_breakdown': breakdown,
            'quality_breakdown': quality_breakdown
        }