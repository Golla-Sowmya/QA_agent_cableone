import os
import sys
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI

# Add the correct path to import RAG_context
sys.path.append(r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator")
from RAG_context import TestCaseRAGContext  # Import the RAG context

from test_case_parser import TestCase, TestCaseRequirement
from test_case_parser import TestCaseParser
from coordinator_agent import CoordinatorAgent
from retrieval_agent import RetrievalAgent  # Updated version
from generation_agent import GenerationAgent  # Updated version

load_dotenv()

class MultiAgentRAGSystem:
    """Enhanced Multi-Agent RAG System with proper RAG context integration"""
    
    def __init__(self, test_cases_directory: str = r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator\test_cases"):
        self.test_cases_dir = Path(test_cases_directory)
        self.parser = TestCaseParser()
        self.test_cases = []
        
        # Initialize RAG context FIRST
        print(" Initializing RAG Context...")
        self.rag_context = TestCaseRAGContext()
        print(f" RAG Context loaded: {len(self.rag_context.chunks)} chunks available")
        
        # Initialize LLM with o1-mini specific settings
        model_name = os.getenv("AZURE_OPENAI_LLM_MODEL", "o1-mini")
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_LLM_MODEL_DEPLOYMENT"),
            model_name=model_name,
            temperature=1 if model_name != "o1-mini" else 0.1,  # o1-mini works better with lower temperature
            max_tokens=4000,
            timeout=60
        )
        
        # Load test cases
        self._load_test_cases()
        
        # Initialize agents with RAG context
        print(" Initializing Enhanced Agents...")
        self.coordinator = CoordinatorAgent(self.llm)
        self.retriever = RetrievalAgent(self.llm, self.test_cases, self.rag_context)  # Pass RAG context
        self.generator = GenerationAgent(self.llm, self.test_cases, self.rag_context)  # Pass RAG context
        
        print(f" Enhanced Multi-Agent System Initialized:")
        print(f"    Coordinator Agent: Ready")
        print(f"    Retrieval Agent: {len(self.test_cases)} test cases + RAG context")
        print(f"    Generation Agent: Template adaptation + RAG context")
        print(f"    RAG Context: {len(self.rag_context.chunks)} business contexts")
    
    def _load_test_cases(self):
        """Load all existing test cases"""
        all_test_cases = []
        
        if not self.test_cases_dir.exists():
            self.test_cases_dir.mkdir(exist_ok=True)
            print(f" Created directory: {self.test_cases_dir}")
        
        txt_files = list(self.test_cases_dir.glob("*.txt"))
        
        if not txt_files:
            print(f"   No .txt files found in {self.test_cases_dir}")
            return
        
        print(f" Loading test cases from: {self.test_cases_dir}")
        for file_path in txt_files:
            try:
                test_cases = self.parser.parse_from_file(file_path)
                if test_cases:
                    all_test_cases.extend(test_cases)
                    print(f" Loaded: {file_path.name}")
            except Exception as e:
                print(f" Error loading {file_path.name}: {e}")
        
        self.test_cases = all_test_cases
        print(f" Total loaded: {len(all_test_cases)} test cases")
        
        if all_test_cases:
            # Show breakdown of available test case types
            breakdown = self.retriever.get_available_test_case_types() if hasattr(self, 'retriever') else {}
            if not breakdown:
                breakdown = {}
                for tc in all_test_cases:
                    key = f"{tc.customer_type}-{tc.scenario_type}-{tc.truck_roll_type}Truck"
                    breakdown[key] = breakdown.get(key, 0) + 1
            
            print(" Available test case types:")
            for key, count in breakdown.items():
                print(f"   {key}: {count}")
    
    async def generate_test_cases(self, user_story: str, additional_requirements: str = "", 
                                number_of_test_cases: int = 4) -> Dict[str, Any]:
        """Main method - multi-agent test case generation orchestration"""
        
        print(f"\n Multi-Agent System: Generating {number_of_test_cases} test cases...")
        print(f"{'='*60}")
        
        # Step 1: Coordinator analyzes requirements
        print(f" STEP 1: Coordinator Agent analyzing requirements...")
        requirements = await self.coordinator.analyze_requirements(
            user_story, additional_requirements, number_of_test_cases
        )
        
        print(f" Coordinator Result: {len(requirements)} requirement types identified")
        for req in requirements:
            print(f"   - {req.customer_type}-{req.scenario_type}-{req.truck_roll_type}Truck (need {req.count_needed})")
        
        # Step 2: Process each requirement with Retrieval and Generation agents
        print(f"\n STEP 2: Processing each requirement...")
        
        all_results = []
        total_retrieved = 0
        total_generated = 0
        generation_details = []
        retrieved_test_case_ids = set()  # Track unique test cases to prevent duplicates
        
        for i, req in enumerate(requirements, 1):
            print(f"\n Requirement {i}: {req.customer_type}-{req.scenario_type}-{req.truck_roll_type}Truck (need {req.count_needed})")
            
            # Try retrieval first
            print(f" Retrieval Agent: Searching for existing test cases...")
            existing_cases = await self.retriever.find_test_cases(req, user_story)
            
            if len(existing_cases) >= req.count_needed:
                # Filter out duplicates and select unique test cases
                unique_cases = []
                for case in existing_cases:
                    if case.id not in retrieved_test_case_ids:
                        unique_cases.append(case)
                        retrieved_test_case_ids.add(case.id)
                        # For consolidated requirements, try to get more cases if available
                        if len(unique_cases) >= req.count_needed and req.count_needed <= 2:
                            break
                
                all_results.extend(unique_cases)
                total_retrieved += len(unique_cases)
                print(f"    Retrieval Complete: Found {len(unique_cases)} unique existing test case(s)")
                if len(existing_cases) > len(unique_cases):
                    print(f"    Note: {len(existing_cases) - len(unique_cases)} cases were duplicates, skipped")
            
            else:
                # Use existing + generate missing - filter duplicates first
                unique_existing_cases = []
                if existing_cases:
                    for case in existing_cases:
                        if case.id not in retrieved_test_case_ids:
                            unique_existing_cases.append(case)
                            retrieved_test_case_ids.add(case.id)
                    
                    all_results.extend(unique_existing_cases)
                    total_retrieved += len(unique_existing_cases)
                    print(f"    Retrieval Partial: Found {len(unique_existing_cases)} unique existing test case(s)")
                    if len(unique_existing_cases) < len(existing_cases):
                        print(f"    Note: {len(existing_cases) - len(unique_existing_cases)} cases were duplicates, skipped")
                
                # Generate missing ones based on unique existing count
                missing_count = req.count_needed - len(unique_existing_cases)
                print(f" Generation Agent: Creating {missing_count} new test case(s)...")
                
                for j in range(missing_count):
                    print(f"    Generating test case {j+1}/{missing_count}...")
                    
                    # Create single requirement for generation
                    single_req = TestCaseRequirement(
                        customer_type=req.customer_type,
                        scenario_type=req.scenario_type,
                        truck_roll_type=req.truck_roll_type,
                        count_needed=1,
                        priority=req.priority
                    )
                    
                    generated_case = await self.generator.generate_test_case(single_req, user_story)
                    
                    if generated_case:
                        all_results.append(generated_case)
                        self.test_cases.append(generated_case)  # Add to collection for future use
                        total_generated += 1
                        
                        # Save generated test case
                        await self._save_generated_test_case(generated_case)
                        
                        generation_details.append({
                            'id': generated_case.id,
                            'type': f"{req.customer_type}-{req.scenario_type}-{req.truck_roll_type}Truck",
                            'template_used': generated_case.template_sources[0] if generated_case.template_sources else 'None',
                            'reasoning': generated_case.generation_reasoning
                        })
                    else:
                        print(f"    Generation failed for test case {j+1}")
        
        # Step 3: Format and return results
        print(f"\n STEP 3: Formatting results...")
        
        # Don't limit results prematurely - let all unique test cases be processed
        # Only limit if we have more results than the requested count for final presentation
        results_to_format = all_results
        if len(all_results) > number_of_test_cases:
            print(f"   Note: System found {len(all_results)} test cases, limiting final output to {number_of_test_cases} for presentation")
            results_to_format = all_results[:number_of_test_cases]
        
        formatted_cases = []
        for tc in results_to_format:
            formatted_case = {
                'id': tc.id,
                'title': tc.title,
                'customer_type': tc.customer_type,
                'customer_status': tc.customer_status,
                'scenario_type': tc.scenario_type,
                'truck_roll_type': tc.truck_roll_type,
                'steps': tc.steps,
                'full_content': tc.content,
                'context': tc.context,
                'is_generated': tc.is_generated
            }
            
            if tc.is_generated:
                formatted_case.update({
                    'template_sources': tc.template_sources,
                    'generation_reasoning': tc.generation_reasoning
                })
            
            formatted_cases.append(formatted_case)
        
        print(f"\n Multi-Agent Process Complete!")
        print(f"{'='*60}")
        print(f" Final Results:")
        print(f"    Requirements Processed: {len(requirements)}")
        print(f"    Unique Test Cases Retrieved: {total_retrieved}")
        print(f"    New Test Cases Generated: {total_generated}")
        print(f"    Total Unique Cases Delivered: {len(formatted_cases)}")
        print(f"    Deduplication: {len(retrieved_test_case_ids)} unique IDs tracked")
        
        return {
            'status': 'success',
            'test_cases': formatted_cases,
            'requirements': requirements,
            'summary': {
                'total_retrieved': total_retrieved,
                'total_generated': total_generated,
                'total_delivered': len(formatted_cases),
                'generation_details': generation_details
            }
        }
    
    async def _save_generated_test_case(self, test_case: TestCase):
        """Save generated test case to file system for future use"""
        try:
            filename = f"{test_case.id}.txt"
            file_path = self.test_cases_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_case.content)
            
            print(f"    Saved to file: {filename}")
            
        except Exception as e:
            print(f"    Save failed: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and capabilities"""
        available_types = self.retriever.get_available_test_case_types()
        
        return {
            'total_test_cases': len(self.test_cases),
            'available_types': available_types,
            'agents_ready': {
                'coordinator': self.coordinator is not None,
                'retriever': self.retriever is not None,
                'generator': self.generator is not None
            },
            'llm_configured': self.llm is not None
        }
    
    def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG integration status"""
        categories = self.rag_context.get_all_categories()
        segments = self.rag_context.get_all_customer_segments()
        
        return {
            'rag_chunks_loaded': len(self.rag_context.chunks),
            'available_categories': categories,
            'available_segments': segments,
            'rag_integration': {
                'coordinator': 'Basic (no RAG needed)',
                'retriever': 'Enhanced (RAG scoring + semantic search)',
                'generator': 'Enhanced (RAG context + template selection)'
            }
        }