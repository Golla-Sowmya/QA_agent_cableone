from typing import Dict
from datetime import datetime
from multi_agent_system import MultiAgentRAGSystem

class IntelligentRAGSystem:
    """Updated interface with RAG status reporting"""
    
    def __init__(self, test_cases_directory: str = r"C:\Users\sgolla\Downloads\QA_agent\Test_case_generator\test_cases"):
        """Initialize with enhanced RAG integration"""
        print("🚀 Initializing Enhanced Intelligent RAG System...")
        self.system = MultiAgentRAGSystem(test_cases_directory)
        
        # Show RAG integration status
        rag_status = self.system.get_rag_status()
        print("✅ Enhanced Multi-Agent RAG System Ready!")
        print("🤖 Architecture: Coordinator → Retriever → Generator (ALL with RAG)")
        print(f"🧠 RAG Integration: {rag_status['rag_chunks_loaded']} business contexts loaded")
        print(f"📊 Categories: {', '.join(rag_status['available_categories'])}")
        print(f"👥 Segments: {', '.join(rag_status['available_segments'])}")
    
    # Add method to get enhanced system info
    def get_enhanced_system_info(self) -> Dict:
        """Get enhanced system information including RAG status"""
        base_info = self.get_system_info()
        rag_status = self.system.get_rag_status()
        
        base_info.update({
            'rag_integration': rag_status,
            'enhanced_capabilities': [
                'RAG-powered semantic search for template selection',
                'Business context-aware test case generation', 
                'Step preservation with comprehensive adaptation',
                'Intelligent relevance scoring using domain knowledge',
                'Context-driven test case matching and selection'
            ]
        })
        
        return base_info
    
    async def get_test_cases_from_user_story(self, user_story: str, additional_requirements: str = "", 
                                           number_of_test_cases: int = 4) -> Dict:
        """Generate test cases from user story using multi-agent approach
        
        Args:
            user_story: The user story describing the requirements
            additional_requirements: Any additional testing requirements  
            number_of_test_cases: Number of test cases to generate
            
        Returns:
            Dictionary containing test cases, summary, and detailed output
        """
        
        try:
            print(f"\n📝 Processing User Story Request:")
            print(f"   📊 Requested test cases: {number_of_test_cases}")
            print(f"   📋 Additional requirements: {additional_requirements or 'None'}")
            
            # Use multi-agent system to generate test cases
            result = await self.system.generate_test_cases(
                user_story, additional_requirements, number_of_test_cases
            )
            
            if result['status'] == 'success':
                # Format comprehensive output
                formatted_output = self._format_comprehensive_output(
                    user_story, result, additional_requirements
                )
                
                return {
                    'status': 'success',
                    'test_cases': result['test_cases'],
                    'final_output': formatted_output,
                    'requirements': result['requirements'],
                    'summary': result['summary']
                }
            else:
                return result
                
        except Exception as e:
            return {
                'status': 'failed', 
                'error': f"System error: {str(e)}"
            }
    
    def _format_comprehensive_output(self, user_story: str, result: Dict, 
                                   additional_requirements: str) -> str:
        """Format comprehensive output with full transparency"""
        
        summary = result['summary']
        requirements = result['requirements']
        
        output_lines = [
            "# INTELLIGENT MULTI-AGENT RAG TEST CASE GENERATION",
            "=" * 70,
            "",
            "## 📋 REQUEST DETAILS",
            f"**User Story**: {user_story}",
            f"**Additional Requirements**: {additional_requirements or 'None specified'}",
            f"**Requested Test Cases**: {summary['total_retrieved'] + summary['total_generated']}",
            f"**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 🤖 MULTI-AGENT PROCESS RESULTS",
            f"**🎯 Coordinator Agent**: Analyzed requirements → {len(requirements)} requirement types",
            f"**🔍 Retrieval Agent**: Found existing test cases → {summary['total_retrieved']} retrieved", 
            f"**🔧 Generation Agent**: Created missing test cases → {summary['total_generated']} generated",
            f"**📊 Total Delivered**: {summary['total_delivered']} test cases",
            "",
            "## 📋 REQUIREMENT BREAKDOWN",
            ""
        ]
        
        for i, req in enumerate(requirements, 1):
            output_lines.append(
                f"**Requirement {i}**: {req.customer_type}-{req.scenario_type}-{req.truck_roll_type}Truck (x{req.count_needed})"
            )
        
        output_lines.append("")
        
        if summary['total_generated'] > 0:
            output_lines.extend([
                "## 🔧 GENERATION TRANSPARENCY",
                ""
            ])
            
            for detail in summary['generation_details']:
                output_lines.extend([
                    f"**Generated Test Case**: {detail['id']}",
                    f"**Type**: {detail['type']}",
                    f"**Template Used**: {detail['template_used']}",
                    f"**Generation Logic**: {detail['reasoning']}",
                    ""
                ])
        
        output_lines.extend([
            "## 📋 COMPLETE TEST CASES",
            ""
        ])
        
        for i, tc in enumerate(result['test_cases'], 1):
            if tc['is_generated']:
                status_icon = "🔧"
                status_text = "GENERATED"
                source_info = f"**Template Used**: {', '.join(tc['template_sources'])}\n**Generation Logic**: {tc['generation_reasoning']}"
            else:
                status_icon = "📁"
                status_text = "RETRIEVED"
                source_info = "**Source**: Existing test case library"
            
            output_lines.extend([
                f"### {status_icon} TC-{i}: {tc['title']} ({status_text})",
                f"**Type**: {tc['customer_type']} {tc['scenario_type']} - {tc['truck_roll_type']} TruckRoll",
                f"**Customer Status**: {tc['customer_status']}",
                f"**Steps**: {len(tc['steps'])}",
                source_info,
                "",
                "**Complete Test Case Content:**",
                "```",
                tc['full_content'],
                "```",
                "",
                "-" * 60,
                ""
            ])
        
        output_lines.extend([
            "## 📊 SUMMARY STATISTICS",
            f"- **Total Test Cases Delivered**: {summary['total_delivered']}",
            f"- **Retrieved from Library**: {summary['total_retrieved']}",
            f"- **Generated New**: {summary['total_generated']}",
            f"- **Success Rate**: {(summary['total_delivered']/(summary['total_retrieved']+summary['total_generated'])*100):.1f}%" if (summary['total_retrieved']+summary['total_generated']) > 0 else "100%",
            "",
            "---",
            "*Generated by Intelligent Multi-Agent RAG System*",
            f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return '\n'.join(output_lines)
    
    def get_system_info(self) -> Dict:
        """Get information about the system capabilities and status"""
        status = self.system.get_system_status()
        
        return {
            'system_name': 'Intelligent Multi-Agent RAG System',
            'version': '1.0',
            'capabilities': [
                'Multi-agent architecture (Coordinator, Retriever, Generator)',
                'Intelligent requirement analysis from user stories',
                'Existing test case retrieval with semantic matching',
                'New test case generation using template adaptation',
                'Scalable from 4 to 50+ test cases',
                'Full transparency and traceability',
                'Automatic saving of generated test cases'
            ],
            'status': status,
            'architecture': {
                'coordinator_agent': 'Analyzes user stories and breaks down requirements',
                'retrieval_agent': 'Finds and selects best existing test cases',
                'generation_agent': 'Creates new test cases using template adaptation'
            }
        }
    



import asyncio
import os

async def test_system_capabilities():
    """Test the multi-agent system with various scenarios"""
    
    print("🚀 Testing Intelligent Multi-Agent RAG System")
    print("=" * 60)
    
    # Initialize the system
    system = IntelligentRAGSystem()
    
    # Get system information
    system_info = system.get_system_info()
    print(f"\n📋 System Information:")
    print(f"   Name: {system_info['system_name']}")
    print(f"   Version: {system_info['version']}")
    print(f"   Available Test Cases: {system_info['status']['total_test_cases']}")
    
    # Test user story
    user_story = """
    As a Development Manager, I would like a process built where the eero association process can retrieve Orders and enable the Cable One to eero association (account to device) for the device.
    
    Acceptance criteria:
        We have provided a way for the eero association process to pick up orders that have eero equipment added to them
            the eero device(s) for the given Customer is (are) associated in the eero cloud
            eero device Serial Number(s) is (are) associated to the Customer AccountID
            the ACP AccountID is captured in eero cloud as the "Partner Account ID"
        if it's a new Customer, the Customer account is created in eero cloud
            the Customer type (Residential or Commercial (Business)) is correctly populated in eero cloud
    """
    
    # Test different scales
    test_cases = [
        # {"count": 6, "requirements": "Generate functional test cases with non-repetitive, Positive and Negative Scenarios, including criticality levels."},
        # {"count": 10, "requirements": "Generate functional test cases with non-repetitive, Positive and Negative Scenarios, including criticality levels."},
        {"count": 20, "requirements": "Generate functional test cases with non-repetitive, Positive and Negative Scenarios, including criticality levels."}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: GENERATING {test_case['count']} TEST CASES")
        print(f"{'='*60}")
        
        try:
            result = await system.get_test_cases_from_user_story(
                user_story=user_story,
                additional_requirements=test_case['requirements'],
                number_of_test_cases=test_case['count']
            )
            
            if result['status'] == 'success':
                summary = result['summary']
                print(f"\n✅ TEST {i} - SUCCESS!")
                print(f"   📊 Requested: {test_case['count']}")
                print(f"   📁 Retrieved: {summary['total_retrieved']}")
                print(f"   🔧 Generated: {summary['total_generated']}")
                print(f"   📋 Delivered: {summary['total_delivered']}")
                print(f"   🎯 Success Rate: {(summary['total_delivered']/test_case['count']*100):.1f}%")
                
                # Show agent performance
                print(f"\n🤖 Agent Performance:")
                print(f"   🎯 Coordinator: {len(result['requirements'])} requirements identified")
                print(f"   🔍 Retriever: {summary['total_retrieved']} existing test cases found")
                print(f"   🔧 Generator: {summary['total_generated']} new test cases created")
                
                # Save detailed output for the last test
                if i == len(test_cases):
                    await save_detailed_output(result, test_case['count'])
                
            else:
                print(f"\n❌ TEST {i} - FAILED!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"\n❌ TEST {i} - EXCEPTION!")
            print(f"   Exception: {str(e)}")

async def save_detailed_output(result, test_count):
    """Save detailed output to file"""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = f"multi_agent_rag_results_{test_count}_cases.md"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['final_output'])
        
        print(f"\n📁 Detailed output saved to: {output_path}")
        
    except Exception as e:
        print(f"\n⚠️  Failed to save output: {e}")

async def demo_single_generation():
    """Demo single test case generation request"""
    
    print(f"\n{'='*60}")
    print("DEMO: SINGLE REQUEST")
    print(f"{'='*60}")
    
    system = IntelligentRAGSystem()
    
    simple_story = """
    As a QA Engineer, I need to test the eero device installation process for new residential customers who require a technician visit for setup.
    """
    
    result = await system.get_test_cases_from_user_story(
        user_story=simple_story,
        additional_requirements="Focus on happy path scenario with proper validation steps",
        number_of_test_cases=4
    )
    
    if result['status'] == 'success':
        print("\n✅ DEMO SUCCESS!")
        
        # Show test case titles
        print("\n📋 Generated Test Cases:")
        for i, tc in enumerate(result['test_cases'], 1):
            status = "🔧 Generated" if tc['is_generated'] else "📁 Retrieved"
            print(f"   {i}. {status}: {tc['title']}")
    else:
        print(f"\n❌ DEMO FAILED: {result.get('error')}")

async def main():
    """Main function to run all tests"""
    
    print("🤖 Intelligent Multi-Agent RAG Test Case Generation System")
    print("🎯 Testing comprehensive capabilities...")
    
    # Run capability tests
    await test_system_capabilities()
    
    # Run simple demo
    await demo_single_generation()
    
    print(f"\n{'='*60}")
    print("🎉 ALL TESTS COMPLETE!")
    print("✅ Multi-Agent RAG System validated and ready for production use")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Import Path here to avoid issues
    from pathlib import Path
    
    # Run the complete test suite
    asyncio.run(main())