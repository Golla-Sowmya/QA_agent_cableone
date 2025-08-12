from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from test_case_parser import TestCase, TestCaseRequirement

class RetrievalAgent:
    """Enhanced Retrieval Agent with RAG context integration"""
    
    def __init__(self, llm: AzureChatOpenAI, test_cases: List[TestCase], rag_context):
        self.llm = llm
        self.test_cases = test_cases
        self.rag_context = rag_context  # Add RAG context
        
        # Enhanced selection prompt with RAG context
# ONLY replace the selection_prompt in retrieval_agent.py

# ONLY replace the selection_prompt in retrieval_agent.py

        self.selection_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Retrieval Agent with expertise in Eero Product Combination matching.

EERO COMBINATION MATCHING EXPERTISE:
- Understand that basic matching (RESI-install-NoTruck) can have multiple product variants
- Recognize when test cases represent different eero product combinations:
  * Base eero service vs Plus/Secure premium service
  * Single device vs multiple device configurations  
  * Standard installation vs enhanced service features
  * Basic CoS vs premium service upgrades

INTELLIGENT SELECTION STRATEGY:
- When multiple test cases match basic criteria, select based on eero product combination relevance
- Prefer test cases that match the specific eero service configuration needed
- Avoid selecting identical basic scenarios when diverse combinations are available
- Prioritize comprehensive test cases that cover specific eero product features

COMBINATION DIVERSITY PRIORITY:
- If selecting multiple test cases of same type, choose different eero product combinations
- Prefer test cases with different service configurations and product features
- Select test cases that provide diverse eero scenario coverage"""),
    
    ("human", """EERO COMBINATION SELECTION:

Looking for: {customer_type} {scenario_type} - {truck_roll_type} TruckRoll
Count needed: {count_needed}
User story context: {user_story_context}

Available matching test cases:
{available_cases}

COMBINATION ANALYSIS:
Analyze the user story to understand what SPECIFIC EERO PRODUCT COMBINATION is needed:
- Is this base eero service or premium plus/secure?
- Is this single device or multiple device scenario?
- Is this standard workflow or enhanced service configuration?

INTELLIGENT SELECTION CRITERIA:
1. **Exact Basic Match**: Must match customer type, scenario, and truck roll
2. **Product Combination Relevance**: Prefer test cases matching specific eero combination from user story
3. **Combination Diversity**: If selecting multiple, choose different eero product combinations
4. **Comprehensive Coverage**: Select test cases with relevant eero service features

IMPORTANT: 
- Avoid selecting multiple identical basic scenarios
- Prioritize test cases that match specific eero product combinations from user story
- Choose diverse eero service configurations when selecting multiple test cases

Respond with ONLY the test case IDs, one per line:
TC_ID_1
TC_ID_2
TC_ID_3

Selected diverse eero combination test cases:""")
])
    
    async def find_test_cases(self, requirement: TestCaseRequirement, 
                            user_story: str) -> List[TestCase]:
        """Enhanced test case finding with RAG context integration"""
        
        # First, get RAG context for this requirement
        rag_analysis = self._get_rag_analysis_for_requirement(requirement, user_story)
        
        # Find exact matches
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
        
        # Enhance matching with RAG scoring
        rag_scored_cases = self._score_cases_with_rag(matching_cases, requirement, user_story)
        
        print(f"   🔍 Found {len(matching_cases)} exact matches, applying RAG analysis...")
        
        if len(rag_scored_cases) <= requirement.count_needed:
            print(f"   ✅ All {len(rag_scored_cases)} matches selected (RAG enhanced)")
            return [tc for _, tc in rag_scored_cases]
        
        # Use LLM with RAG context for intelligent selection
        print(f"   🧠 Using LLM + RAG for intelligent selection of {requirement.count_needed} from {len(rag_scored_cases)}")
        
        try:
            # Format available cases with RAG scores
            available_text = ""
            for score, tc in rag_scored_cases:
                available_text += f"{tc.id} (RAG Score: {score}/100)\n"
                available_text += f"Title: {tc.title}\n"
                available_text += f"Steps: {len(tc.steps)}\n"
                available_text += f"Content preview: {tc.content[:200]}...\n"
                available_text += "-" * 40 + "\n\n"
            
            chain = self.selection_prompt | self.llm
            response = await chain.ainvoke({
                'customer_type': requirement.customer_type,
                'scenario_type': requirement.scenario_type,
                'truck_roll_type': requirement.truck_roll_type,
                'count_needed': requirement.count_needed,
                'user_story_context': user_story[:500],
                'rag_context': rag_analysis,
                'available_cases': available_text[:3000]  # Reasonable limit
            })
            
            # Parse selected IDs
            selected_ids = [line.strip() for line in response.content.strip().split('\n') 
                          if line.strip() and line.strip().startswith('TC_')]
            
            # Find selected test cases in RAG-scored list
            selected_cases = []
            for tc_id in selected_ids:
                for score, tc in rag_scored_cases:
                    if tc.id == tc_id and tc not in selected_cases:
                        selected_cases.append(tc)
                        print(f"     📝 Selected: {tc.id} (RAG Score: {score})")
                        break
            
            if len(selected_cases) >= requirement.count_needed:
                result = selected_cases[:requirement.count_needed]
                print(f"   ✅ LLM + RAG selected {len(result)} best matches")
                return result
            else:
                # Fallback to top RAG-scored cases
                result = [tc for _, tc in rag_scored_cases[:requirement.count_needed]]
                print(f"   ✅ Using top {len(result)} RAG-scored matches (LLM fallback)")
                return result
                
        except Exception as e:
            print(f"   ⚠️  Enhanced selection failed: {e}, using top RAG-scored matches")
            result = [tc for _, tc in rag_scored_cases[:requirement.count_needed]]
            return result
    
    def _get_rag_analysis_for_requirement(self, requirement: TestCaseRequirement, user_story: str) -> str:
        """Get comprehensive RAG analysis for the requirement"""
        
        # Search by multiple criteria
        search_results = []
        
        # 1. Search by customer segment
        segment = 'residential' if requirement.customer_type == 'RESI' else 'business'
        segment_contexts = self.rag_context.get_context_by_customer_segment(segment)
        search_results.extend(segment_contexts)
        
        # 2. Search by test category
        category = 'install' if requirement.scenario_type == 'install' else 'change_of_service'
        category_contexts = self.rag_context.get_context_by_category(category)
        search_results.extend(category_contexts)
        
        # 3. Search by keywords from user story
        story_keywords = [word.lower() for word in user_story.split() 
                         if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with']]
        for keyword in story_keywords[:5]:
            keyword_contexts = self.rag_context.search_context(keyword)
            search_results.extend(keyword_contexts)
        
        # Remove duplicates and format
        unique_contexts = {ctx.get('file_name', 'unknown'): ctx for ctx in search_results}
        
        if not unique_contexts:
            return "No specific RAG context found - using general matching criteria."
        
        analysis_text = "## RAG BUSINESS CONTEXT ANALYSIS:\n\n"
        for i, (filename, ctx) in enumerate(list(unique_contexts.items())[:4], 1):
            analysis_text += f"**Relevant Context {i}**:\n"
            analysis_text += f"- **File**: {ctx.get('file_name', 'N/A')}\n"
            analysis_text += f"- **Business Purpose**: {ctx.get('business_purpose', 'N/A')}\n"
            analysis_text += f"- **Context Summary**: {ctx.get('context_summary', 'N/A')}\n"
            analysis_text += f"- **Keywords**: {', '.join(ctx.get('keywords', []))}\n"
            analysis_text += f"- **Test Category**: {ctx.get('test_category', 'N/A')}\n\n"
        
        return analysis_text
    
    def _score_cases_with_rag(self, test_cases: List[TestCase], requirement: TestCaseRequirement, 
                             user_story: str) -> List[tuple]:
        """Score test cases using RAG context relevance"""
        
        # Get relevant RAG contexts
        segment = 'residential' if requirement.customer_type == 'RESI' else 'business'
        category = 'install' if requirement.scenario_type == 'install' else 'change_of_service'
        
        relevant_contexts = []
        relevant_contexts.extend(self.rag_context.get_context_by_customer_segment(segment))
        relevant_contexts.extend(self.rag_context.get_context_by_category(category))
        
        # Create set of relevant filenames
        relevant_filenames = set()
        for ctx in relevant_contexts:
            filename = ctx.get('file_name', '').replace('.txt', '')
            if filename:
                relevant_filenames.add(filename)
        
        # Score each test case
        scored_cases = []
        for tc in test_cases:
            score = 0
            
            # RAG relevance scoring (50 points)
            tc_filename = tc.id.replace('TC_', '')
            rag_matches = sum(1 for filename in relevant_filenames 
                            if filename in tc_filename or tc_filename in filename)
            if rag_matches > 0:
                score += min(50, rag_matches * 25)  # Up to 50 points for RAG relevance
            
            # Quality scoring (30 points)
            if len(tc.steps) > 15:
                score += 20
            elif len(tc.steps) > 10:
                score += 15
            elif len(tc.steps) > 5:
                score += 10
            
            if len(tc.content) > 3000:
                score += 10
            elif len(tc.content) > 1500:
                score += 5
            
            # Context richness (20 points)
            if tc.context:
                score += 10
            
            if 'api' in tc.content.lower():
                score += 5
            if 'verification' in tc.content.lower():
                score += 5
            
            scored_cases.append((score, tc))
        
        # Sort by score (highest first)
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        
        print(f"   📊 RAG scoring complete - top scores: {[s for s, _ in scored_cases[:3]]}")
        return scored_cases
    
    def get_available_test_case_types(self) -> dict:
        """Get breakdown of available test case types"""
        breakdown = {}
        for tc in self.test_cases:
            if not tc.is_generated:
                key = f"{tc.customer_type}-{tc.scenario_type}-{tc.truck_roll_type}Truck"
                breakdown[key] = breakdown.get(key, 0) + 1
        return breakdown