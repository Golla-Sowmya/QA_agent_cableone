from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class RetrievalAgent:
    """Enhanced Retrieval Agent with emphasis on complete workflow templates"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context
        
        # Simplified selection prompt for template finding
        self.selection_prompt = ChatPromptTemplate.from_messages([
            ("system", """You find the best test case templates for adaptation.

**YOUR TASK:**
Select templates that:
1. Match the customer type (RESI/BUSI), scenario (install/cos), and truck roll
2. Have detailed steps (prefer 8+ steps with clear instructions)
3. Include complete workflows with expected results
4. Can be adapted for different service codes
5. Provide diversity - avoid selecting the same templates repeatedly

**QUALITY PRIORITIES:**
- More detailed steps = better template
- Complete workflows with validations = better template
- Clear expected results = better template
- Templates that match business context = better template
- Unused/less frequently selected templates = better for diversity

**SERVICE CODE AWARENESS:**
- RESI templates can be adapted for HE*** service codes
- BUSI Install templates can be adapted for BHSY1-BHSY3 codes
- BUSI CoS templates must be compatible with BHSY5/BHSY6 (W2W, Additional)
- Avoid templates that conflict with BUSI CoS service constraints

**DIVERSITY REQUIREMENTS:**
- Don't select the same template multiple times in one session
- Prefer templates that haven't been used recently
- If multiple similar templates exist, rotate selection
- Provide variety in template sources for better test coverage

**SELECTION APPROACH:**
- Find exact matches first (same customer type, scenario, truck roll)
- Prioritize templates with more detailed steps
- Consider business context relevance and service code compatibility
- Enforce diversity by avoiding repeated template selection"""),
            
            ("human", """**FIND TEMPLATES FOR:**
- Customer: {customer_type}
- Scenario: {scenario_type}
- Truck Roll: {truck_roll_type}
- Need: {count_needed} templates

**BUSINESS CONTEXT:**
{rag_context}

**AVAILABLE TEMPLATES:**
{available_cases}

**SELECTION CRITERIA:**
1. **Exact Match**: Same customer type, scenario, and truck roll
2. **Step Quality**: Prefer templates with more detailed steps (8+ is best)
3. **Completeness**: Templates should have complete workflows with expected results
4. **Business Fit**: Templates that match the business context above
5. **Service Code Compatibility**: Templates adaptable to required service codes
6. **Diversity**: Avoid selecting templates that appear multiple times in the list

**AVOID REPETITION:**
If you see the same template ID appearing multiple times in the available list, select it only ONCE. Choose different templates to provide variety.

**YOUR TASK:**
Review the available templates and select the {count_needed} best ones that:
- Match the requirements exactly
- Have detailed step-by-step workflows
- Include clear expected results
- Can be adapted for the target combination

**SERVICE CODE COMPATIBILITY:**
- {customer_type} customers need templates adaptable to their service code pattern
- Templates should have similar workflow structures for adaptation

Select the {count_needed} best template IDs:""")
        ])

    async def find_test_cases(self, requirement: TestCaseRequirement, 
                            user_story: str) -> List[TestCase]:
        """Enhanced retrieval prioritizing complete workflow templates"""
        
        print(f"    Searching for COMPLETE workflow templates...")
        
        # Find basic matching cases first
        matching_cases = [
            tc for tc in self.test_cases
            if (tc.customer_type == requirement.customer_type and
                tc.scenario_type == requirement.scenario_type and
                tc.truck_roll_type == requirement.truck_roll_type and
                not tc.is_generated)
        ]
        
        if not matching_cases:
            print(f"    No exact matches found")
            return []
        
        print(f"    Found {len(matching_cases)} matches, filtering for completeness...")
        
        # Filter for complete templates (8+ steps minimum)
        complete_templates = [tc for tc in matching_cases if len(tc.steps) >= 8]
        
        if not complete_templates:
            print(f"     No complete templates found (8+ steps), using best available")
            complete_templates = sorted(matching_cases, key=lambda tc: len(tc.steps), reverse=True)
        
        print(f"    Found {len(complete_templates)} complete templates")
        
        # Score templates with service code awareness
        complete_scored_cases = self._score_template_completeness(complete_templates, requirement, user_story)
        
        if len(complete_scored_cases) <= requirement.count_needed:
            selected = [tc for _, tc in complete_scored_cases]
            print(f"    Selected all {len(selected)} complete templates")
            for tc in selected:
                print(f"      {tc.id}: {len(tc.steps)} steps (Complete workflow)")
            return selected
        
        # Use LLM for intelligent selection among complete templates
        print(f"    Using LLM for optimal complete template selection")
        
        try:
            rag_context_text = self._get_rag_context_for_retrieval(requirement, user_story)
            combination_context = self._get_combination_context_for_retrieval(requirement, user_story)
            available_cases_text = self._format_complete_templates(complete_scored_cases, requirement)
            
            chain = self.selection_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type,
                'truck_roll_type': requirement.truck_roll_type,
                'count_needed': requirement.count_needed,
                'rag_context': rag_context_text,
                'combination_context': combination_context,
                'available_cases': available_cases_text
            })
            
            # Parse selected IDs
            selected_ids = [line.strip() for line in response.content.strip().split('\n') 
                          if line.strip() and line.strip().startswith('TC_')]
            
            # Find selected test cases
            selected_cases = []
            for tc_id in selected_ids:
                for score, tc in complete_scored_cases:
                    if tc.id == tc_id and tc not in selected_cases:
                        selected_cases.append(tc)
                        print(f"      Selected: {tc.id} ({len(tc.steps)} steps - Complete workflow)")
                        break
            
            if len(selected_cases) >= requirement.count_needed:
                result = selected_cases[:requirement.count_needed]
                print(f"    LLM selected {len(result)} complete workflow templates")
                return result
            else:
                result = [tc for _, tc in complete_scored_cases[:requirement.count_needed]]
                print(f"    Using top {len(result)} complete templates (LLM fallback)")
                return result
                
        except Exception as e:
            print(f"     Enhanced selection failed: {e}, using top complete templates")
            result = [tc for _, tc in complete_scored_cases[:requirement.count_needed]]
            return result
    
    def _score_template_completeness(self, test_cases: List[TestCase], 
                                   requirement: TestCaseRequirement, 
                                   user_story: str) -> List[tuple]:
        """Score templates with heavy emphasis on completeness"""
        
        scored_cases = []
        
        for tc in test_cases:
            score = 0
            content_lower = tc.content.lower()
            
            # Template completeness scoring (50 points - highest priority)
            step_count = len(tc.steps)
            if step_count >= 12:
                score += 50  # Excellent completeness
            elif step_count >= 10:
                score += 45  # Very good completeness
            elif step_count >= 8:
                score += 40  # Good completeness
            elif step_count >= 6:
                score += 30  # Acceptable completeness
            else:
                score += 15  # Poor completeness
            
            # Step detail quality (20 points)
            avg_step_length = sum(len(step.get('action', '')) for step in tc.steps) / max(1, len(tc.steps))
            if avg_step_length > 100:
                score += 20  # Very detailed steps
            elif avg_step_length > 60:
                score += 15  # Good detail
            elif avg_step_length > 30:
                score += 10  # Basic detail
            else:
                score += 5   # Poor detail
            
            # Expected results coverage (15 points)
            steps_with_results = sum(1 for step in tc.steps if step.get('expected_result', '').strip())
            result_coverage = steps_with_results / max(1, len(tc.steps))
            score += int(result_coverage * 15)
            
            # Workflow indicators (15 points)
            workflow_indicators = ['acsr', 'customer central', 'order', 'verification', 'expected result']
            indicator_score = sum(3 for indicator in workflow_indicators if indicator in content_lower)
            score += min(15, indicator_score)
            
            scored_cases.append((score, tc))
        
        # Sort by score (highest first)
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        # Log scoring results with completeness focus
        print(f"    Template completeness scoring:")
        for score, tc in scored_cases[:3]:
            completeness_level = "EXCELLENT" if score >= 90 else "VERY GOOD" if score >= 80 else "GOOD" if score >= 70 else "ACCEPTABLE"
            print(f"     {tc.id}: {score}/100 ({len(tc.steps)} steps - {completeness_level})")
        
        return scored_cases
    
    def _format_complete_templates(self, scored_cases: List[tuple], 
                                 requirement: TestCaseRequirement) -> str:
        """Format templates with emphasis on completeness indicators"""
        text = ""
        
        for score, tc in scored_cases[:8]:  # Top 8 complete templates
            completeness_level = "EXCELLENT" if score >= 90 else "VERY GOOD" if score >= 80 else "GOOD" if score >= 70 else "ACCEPTABLE"
            
            text += f"{tc.id} (Completeness: {completeness_level}, Score: {score}/100)\n"
            text += f"Title: {tc.title}\n"
            text += f"Steps: {len(tc.steps)} (Detailed workflow)\n"
            text += f"Customer: {tc.customer_type} {tc.customer_status}\n"
            text += f"Scenario: {tc.scenario_type}\n"
            text += f"Truck Roll: {tc.truck_roll_type}\n"
            
            # Add completeness indicators
            steps_with_results = sum(1 for step in tc.steps if step.get('expected_result', '').strip())
            result_coverage = int((steps_with_results / max(1, len(tc.steps))) * 100)
            text += f"Expected Results Coverage: {result_coverage}%\n"
            
            # Show workflow completeness
            content_lower = tc.content.lower()
            workflow_completeness = []
            if 'acsr' in content_lower:
                workflow_completeness.append("ACSR")
            if 'order' in content_lower and 'details' in content_lower:
                workflow_completeness.append("Order Processing")
            if any(word in content_lower for word in ['verification', 'validate', 'verify']):
                workflow_completeness.append("Verification")
            
            if workflow_completeness:
                text += f"Workflow Components: {', '.join(workflow_completeness)}\n"
            
            text += f"Content preview: {tc.content[:150]}...\n"
            text += "-" * 60 + "\n\n"
        
        return text[:4000]  # Limit for LLM context# COMPLETE ENHANCED GENERATION_AGENT.PY FILE

    
    def _score_with_rag_context(self, test_cases: List[TestCase], 
                               requirement: TestCaseRequirement, 
                               user_story: str) -> List[tuple]:
        """Score test cases using RAG context and combination intelligence"""
        
        scored_cases = []
        
        # Get combination intelligence if available
        combination_type = 'base_eero'
        if self.rag_context:
            try:
                combo_intel = self.rag_context.get_combination_intelligence(user_story)
                combination_type = combo_intel.get('detected_combination', 'base_eero')
            except:
                pass
        
        for tc in test_cases:
            score = 0
            content_lower = tc.content.lower()
            
            # Basic quality scoring (30 points)
            step_count = len(tc.steps)
            if step_count >= 10:
                score += 20
            elif step_count >= 8:
                score += 15
            elif step_count >= 6:
                score += 10
            
            if len(tc.content) > 3000:
                score += 10
            elif len(tc.content) > 2000:
                score += 5
            
            # RAG-based combination compatibility (40 points)
            if combination_type == "eero_plus":
                if any(word in content_lower for word in ["plus", "premium", "security", "enhanced"]):
                    score += 40
                elif "eero" in content_lower and not any(word in content_lower for word in ["multiple", "additional"]):
                    score += 25
            elif combination_type == "multiple_devices":
                if any(word in content_lower for word in ["multiple", "additional", "mesh", "devices"]):
                    score += 40
                elif "eero" in content_lower:
                    score += 20
            elif combination_type == "base_eero":
                if "eero" in content_lower and not any(word in content_lower for word in ["plus", "multiple", "additional"]):
                    score += 40
                elif "eero" in content_lower:
                    score += 25
            
            # Business context alignment (30 points)
            if self.rag_context:
                try:
                    # Get relevant business contexts
                    story_keywords = [word.lower() for word in user_story.split() 
                                    if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that']]
                    
                    context_score = 0
                    for keyword in story_keywords[:5]:
                        contexts = self.rag_context.search_context(keyword)
                        for ctx in contexts[:2]:
                            keywords = ctx.get('keywords', [])
                            if any(kw.lower() in content_lower for kw in keywords):
                                context_score += 3
                    
                    score += min(30, context_score)
                except:
                    score += 15  # Default business context score
            
            scored_cases.append((score, tc))
        
        # Sort by score (highest first)
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        # Log top scored cases
        print(f"    RAG-enhanced scoring:")
        for score, tc in scored_cases[:3]:
            business_alignment = "HIGH" if score >= 80 else "MEDIUM" if score >= 60 else "LOW"
            print(f"     {tc.id}: {score}/100 ({business_alignment} business alignment)")
        
        return scored_cases
    
    def _get_rag_context_for_retrieval(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get relevant RAG context for template retrieval"""
        if not self.rag_context:
            return "No specific business context available for retrieval."
        
        context_text = "## BUSINESS CONTEXT FOR RETRIEVAL:\n\n"
        
        try:
            # Get customer segment specific contexts
            segment = 'residential' if requirement.customer_type == 'RESI' else 'business'
            segment_contexts = self.rag_context.get_context_by_customer_segment(segment)
            
            if segment_contexts:
                context_text += f"**{segment.title()} Segment Requirements:**\n"
                for ctx in segment_contexts[:2]:
                    context_text += f"- Purpose: {ctx.get('business_purpose', 'Standard requirements')}\n"
                    context_text += f"- Category: {ctx.get('test_category', 'General')}\n"
                    context_text += f"- Keywords: {', '.join(ctx.get('keywords', []))}\n"
            
            # Get scenario specific contexts
            scenario_contexts = self.rag_context.get_context_by_category(requirement.scenario_type)
            if scenario_contexts:
                context_text += f"\n**{requirement.scenario_type.title()} Scenario Patterns:**\n"
                for ctx in scenario_contexts[:2]:
                    context_text += f"- Validation: {ctx.get('business_purpose', 'Standard validation')}\n"
                    context_text += f"- Focus: {ctx.get('primary_scenario', 'General workflow')}\n"
            
            # Get story-specific contexts
            story_keywords = [word.lower() for word in user_story.split() 
                            if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that']]
            
            relevant_contexts = []
            for keyword in story_keywords[:5]:
                contexts = self.rag_context.search_context(keyword)
                relevant_contexts.extend(contexts[:1])
            
            if relevant_contexts:
                context_text += f"\n**Story-Specific Business Requirements:**\n"
                unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in relevant_contexts[:3]}
                for ctx in unique_contexts.values():
                    context_text += f"- {ctx.get('business_purpose', 'Standard business validation')}\n"
            
        except Exception as e:
            context_text += f"Standard business requirements apply. (RAG error: {e})\n"
        
        return context_text
    
    def _get_combination_context_for_retrieval(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get combination context for template retrieval with device lifecycle intelligence"""
        if not self.rag_context:
            return "## COMBINATION CONTEXT:\n\nStandard eero combination requirements."
        
        try:
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            
            context_text = f"## COMBINATION INTELLIGENCE FOR RETRIEVAL:\n\n"
            context_text += f"**Detected Pattern:** {combo_intel.get('detected_combination', 'base_eero')}\n"
            context_text += f"**Workflow Type:** {combo_intel.get('workflow_type', 'standard_workflow')}\n"
            
            # Device lifecycle detection
            story_lower = user_story.lower()
            association_keywords = ["association", "associate", "binding", "bind", "device management", "account-to-device", "partner account"]
            if any(keyword in story_lower for keyword in association_keywords):
                context_text += f"**Device Lifecycle Required:** Association process detected - templates must support device removal scenarios\n"
                context_text += f"**Critical Combinations Needed:** Business removal scenarios (IDs 29-31) for comprehensive testing\n"
            
            # Get product requirements
            product_info = combo_intel.get('product_info', {})
            if product_info:
                context_text += f"\n**Product Requirements:**\n"
                context_text += f"- Service Codes: {', '.join(product_info.get('service_codes', ['HE008']))}\n"
                context_text += f"- Features: {', '.join(product_info.get('features', ['basic_wifi']))}\n"
                context_text += f"- Validation Points: {', '.join(product_info.get('validation_points', ['basic_connectivity']))}\n"
            
            # Get adaptation requirements
            modification_rules = combo_intel.get('modification_rules', {})
            if modification_rules:
                context_text += f"\n**Template Adaptation Requirements:**\n"
                context_text += f"- Templates must be adaptable for above service codes and features\n"
                context_text += f"- Must support required validation patterns\n"
            
        except Exception as e:
            context_text = f"## COMBINATION CONTEXT:\n\nStandard eero requirements. (Intelligence error: {e})"
        
        return context_text
    
    def _format_available_cases_with_context(self, scored_cases: List[tuple], 
                                           requirement: TestCaseRequirement) -> str:
        """Format available cases with business context scoring"""
        text = ""
        
        for score, tc in scored_cases[:10]:  # Top 10 cases
            business_alignment = "HIGH" if score >= 80 else "MEDIUM" if score >= 60 else "LOW"
            
            text += f"{tc.id} (Score: {score}/100, Business Alignment: {business_alignment})\n"
            text += f"Title: {tc.title}\n"
            text += f"Steps: {len(tc.steps)}\n"
            text += f"Customer: {tc.customer_type} {tc.customer_status}\n"
            text += f"Scenario: {tc.scenario_type}\n"
            text += f"Truck Roll: {tc.truck_roll_type}\n"
            
            # Add business relevance indicators
            if self.rag_context:
                try:
                    content_lower = tc.content.lower()
                    business_indicators = []
                    if any(word in content_lower for word in ["plus", "premium", "security"]):
                        business_indicators.append("Eero Plus compatible")
                    if any(word in content_lower for word in ["multiple", "additional", "mesh"]):
                        business_indicators.append("Multi-device capable")
                    if any(word in content_lower for word in ["kafka", "api", "insight"]):
                        business_indicators.append("Complete validation")
                    
                    if business_indicators:
                        text += f"Business Features: {', '.join(business_indicators)}\n"
                except:
                    pass
            
            text += f"Content preview: {tc.content[:200]}...\n"
            text += "-" * 60 + "\n\n"
        
        return text[:4000]  # Limit for LLM context
    
    def _assess_business_alignment(self, tc: TestCase, rag_context: str) -> str:
        """Assess how well a template aligns with business context"""
        content_lower = tc.content.lower()
        context_lower = rag_context.lower()
        
        alignment_score = 0
        
        # Check for business terms alignment
        business_terms = ['validation', 'verification', 'business', 'customer', 'service']
        alignment_score += sum(1 for term in business_terms if term in content_lower)
        
        # Check for context keyword alignment
        if 'keywords:' in context_lower:
            try:
                context_section = context_lower.split('keywords:')[1].split('\n')[0]
                context_keywords = [kw.strip() for kw in context_section.split(',') if kw.strip()]
                alignment_score += sum(1 for kw in context_keywords[:5] if kw in content_lower)
            except:
                pass
        
        # Check for workflow completeness
        workflow_indicators = ['kafka', 'api', 'insight', 'endpoint', 'validation']
        alignment_score += sum(1 for indicator in workflow_indicators if indicator in content_lower)
        
        if alignment_score >= 8:
            return "EXCELLENT"
        elif alignment_score >= 5:
            return "GOOD"
        elif alignment_score >= 3:
            return "FAIR"
        else:
            return "BASIC"
    
    def get_available_test_case_types(self) -> dict:
        """Get breakdown of available test case types with RAG enhancement"""
        breakdown = {}
        rag_enhanced_breakdown = {}
        
        for tc in self.test_cases:
            if not tc.is_generated:
                key = f"{tc.customer_type}-{tc.scenario_type}-{tc.truck_roll_type}Truck"
                breakdown[key] = breakdown.get(key, 0) + 1
                
                # Add RAG-based enhancement indicators
                if self.rag_context:
                    try:
                        content_lower = tc.content.lower()
                        enhancements = []
                        if any(word in content_lower for word in ["plus", "premium"]):
                            enhancements.append("Plus")
                        if any(word in content_lower for word in ["multiple", "additional"]):
                            enhancements.append("Multi")
                        if any(word in content_lower for word in ["kafka", "api", "insight"]):
                            enhancements.append("Complete")
                        
                        if enhancements:
                            enhanced_key = f"{key}-{'-'.join(enhancements)}"
                            rag_enhanced_breakdown[enhanced_key] = rag_enhanced_breakdown.get(enhanced_key, 0) + 1
                    except:
                        pass
        
        return {
            'basic_breakdown': breakdown,
            'rag_enhanced_breakdown': rag_enhanced_breakdown
        }