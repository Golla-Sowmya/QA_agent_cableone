from RAG_context import rag_context
from test_case_parser import TestCaseRequirement

class EeroCombinationDetector:
    """Enhanced system to detect and match the 31 specific eero combinations"""
    
    def __init__(self):
        # Define the exact 30 combinations from your table
        self.rag_context = rag_context
        self.valid_combinations = [
            # Install - New - Residential
            {"id": 1, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "with", "eero_type": "eero", "description": "Install New Residential Truck roll Eero"},
            {"id": 2, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "with", "eero_type": "eero_plus", "description": "Install New Residential Truck roll Eero Plus"},
            {"id": 3, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "no", "eero_type": "eero", "description": "Install New Residential No Truck roll Eero"},
            {"id": 4, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "no", "eero_type": "eero_plus", "description": "Install New Residential No Truck roll Eero Plus"},
            {"id": 5, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "with", "eero_type": "eero_additional", "description": "Install New Residential Truck roll Eero + Additional Eero Device"},
            {"id": 6, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "with", "eero_type": "eero_plus_additional", "description": "Install New Residential Truck roll Eero Plus + Additional Eero Device"},
            {"id": 7, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "no", "eero_type": "eero_additional", "description": "Install New Residential No Truck roll Eero + Additional Eero Device"},
            {"id": 8, "order_type": "install", "customer_status": "new", "segment": "residential", "truck_roll": "no", "eero_type": "eero_plus_additional", "description": "Install New Residential No Truck roll Eero Plus + Additional Eero Device"},
            
            # Install - New - Business
            {"id": 9, "order_type": "install", "customer_status": "new", "segment": "business", "truck_roll": "with", "eero_type": "eero", "description": "Install New Business Truck roll Eero"},
            {"id": 10, "order_type": "install", "customer_status": "new", "segment": "business", "truck_roll": "no", "eero_type": "eero", "description": "Install New Business No Truck roll Eero"},
            {"id": 11, "order_type": "install", "customer_status": "new", "segment": "business", "truck_roll": "with", "eero_type": "eero_additional", "description": "Install New Business Truck roll Eero + Additional Eero Device"},
            {"id": 12, "order_type": "install", "customer_status": "new", "segment": "business", "truck_roll": "no", "eero_type": "eero_additional", "description": "Install New Business No Truck roll Eero + Additional Eero Device"},
            
            # Change of Service - Existing - Residential  
            {"id": 13, "order_type": "cos", "customer_status": "existing_hsd", "segment": "residential", "truck_roll": "with", "eero_type": "add_eero", "description": "Change of Service Existing HSD customer Residential Truck roll Add Eero Service"},
            {"id": 14, "order_type": "cos", "customer_status": "existing_hsd", "segment": "residential", "truck_roll": "no", "eero_type": "add_eero", "description": "Change of Service Existing HSD customer Residential No Truck roll Add Eero Service"},
            {"id": 15, "order_type": "cos", "customer_status": "existing_hsd_eero", "segment": "residential", "truck_roll": "no", "eero_type": "remove_eero", "description": "Change of Service Existing HSD customer with Eero Residential No Truck roll Remove Eero Service"},
            {"id": 16, "order_type": "cos", "customer_status": "existing_hsd_eero", "segment": "residential", "truck_roll": "no", "eero_type": "add_additional", "description": "Change of Service Existing HSD customer with Eero Residential No Truck roll Add Additional Eero Device"},
            {"id": 17, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "residential", "truck_roll": "no", "eero_type": "remove_device_not_gateway", "description": "Change of Service Existing HSD customer with Eero and additional Eero Residential No Truck roll Remove Eero device which is gateway No"},
            {"id": 18, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "residential", "truck_roll": "no", "eero_type": "remove_device_gateway", "description": "Change of Service Existing HSD customer with Eero and additional Eero Residential No Truck roll Remove Eero device which is gateway Yes"},
            {"id": 19, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "residential", "truck_roll": "no", "eero_type": "remove_eero_service_device", "description": "Change of Service Existing HSD customer with Eero and additional Eero Residential No Truck roll Remove Eero service along with Device"},
            {"id": 20, "order_type": "cos", "customer_status": "existing_hsd", "segment": "residential", "truck_roll": "with", "eero_type": "add_eero_plus", "description": "Change of Service Existing HSD customer Residential Truck roll Add Eero Plus Service"},
            {"id": 21, "order_type": "cos", "customer_status": "existing_hsd", "segment": "residential", "truck_roll": "no", "eero_type": "add_eero_plus", "description": "Change of Service Existing HSD customer Residential No Truck roll Add Eero Plus Service"},
            {"id": 22, "order_type": "cos", "customer_status": "existing_hsd_eero_plus", "segment": "residential", "truck_roll": "no", "eero_type": "remove_eero_plus", "description": "Change of Service Existing HSD customer with Eero Plus Residential No Truck roll Remove Eero Plus Service"},
            {"id": 23, "order_type": "cos", "customer_status": "existing_hsd_eero", "segment": "residential", "truck_roll": "no", "eero_type": "add_eero_plus_upgrade", "description": "Change of Service Existing HSD customer with Eero Residential No Truck roll Add Eero Plus Service"},
            {"id": 24, "order_type": "cos", "customer_status": "existing_hsd_eero_plus", "segment": "residential", "truck_roll": "no", "eero_type": "remove_eero_eero_plus", "description": "Change of Service Existing HSD customer with Eero Plus Residential No Truck roll Remove Eero and Eero Plus Service"},
            
            # Change of Service - Existing - Business
            {"id": 25, "order_type": "cos", "customer_status": "existing_hsd", "segment": "business", "truck_roll": "with", "eero_type": "add_eero", "description": "Change of Service Existing HSD customer Business Truck roll Add Eero Service"},
            {"id": 26, "order_type": "cos", "customer_status": "existing_hsd", "segment": "business", "truck_roll": "no", "eero_type": "add_eero", "description": "Change of Service Existing HSD customer Business No Truck roll Add Eero Service"},
            {"id": 27, "order_type": "cos", "customer_status": "existing_hsd_eero", "segment": "business", "truck_roll": "no", "eero_type": "remove_eero", "description": "Change of Service Existing HSD customer with Eero Business No Truck roll Remove Eero Service"},
            {"id": 28, "order_type": "cos", "customer_status": "existing_hsd_eero", "segment": "business", "truck_roll": "no", "eero_type": "add_additional", "description": "Change of Service Existing HSD customer with Eero Business No Truck roll Add Additional Eero Device"},
            {"id": 29, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "business", "truck_roll": "no", "eero_type": "remove_device_not_gateway", "description": "Change of Service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero device which is gateway No"},
            {"id": 30, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "business", "truck_roll": "no", "eero_type": "remove_device_gateway", "description": "Change of Service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero device which is gateway Yes"},
            {"id": 31, "order_type": "cos", "customer_status": "existing_hsd_eero_additional", "segment": "business", 'truck_roll': "no", "eero_type": "remove_eero_along_device", "description": "Change of service Existing HSD customer with Eero and additional Eero Business No Truck roll Remove Eero service along with Device "}
        ]
        
        # Service code mappings
        self.service_code_mapping = {
            "eero": "HE008",
            "eero_plus": "HE009", 
            "eero_secure": "HE010",
            "eero_additional": "HE008_MULTI",
            "eero_plus_additional": "HE009_MULTI",
            "add_eero": "HE008",
            "add_eero_plus": "HE009",
            "remove_eero": "REMOVE_HE008",
            "remove_eero_plus": "REMOVE_HE009",
            "add_additional": "ADD_HE008_DEVICE",
            "remove_device_not_gateway": "REMOVE_DEVICE_NON_GATEWAY",
            "remove_device_gateway": "REMOVE_DEVICE_GATEWAY",
            "remove_eero_service_device": "REMOVE_HE008_ALL"
        }
    
    def detect_combinations_from_story(self, user_story: str, requested_count: int = None) -> list:
        """Detect which of the 30 combinations are being requested using both rule-based and RAG context"""
        story_lower = user_story.lower()
        detected_combinations = []
        
        # Extract key information from user story
        story_analysis = self._analyze_user_story(story_lower)
        
        # Get RAG context insights
        rag_insights = self._get_rag_context_insights(user_story) if self.rag_context else {}
        
        # Determine intelligent count if not provided
        if requested_count is None:
            requested_count = self.determine_test_case_count(user_story, story_analysis)
            print(f"   Intelligent count detection: {requested_count} test cases needed")
        
        print(f"   Story Analysis: {story_analysis}")
        print(f"   RAG Insights: Found {len(rag_insights.get('relevant_contexts', []))} relevant contexts")
        
        # Find matching combinations
        for combo in self.valid_combinations:
            match_score = self._calculate_match_score(combo, story_analysis, rag_insights)
            if match_score > 0.4:  # Lower threshold to get more matches
                detected_combinations.append({
                    "combination": combo,
                    "match_score": match_score,
                    "service_code": self.service_code_mapping.get(combo["eero_type"], "HE008"),
                    "rag_context": rag_insights.get('business_purpose', '')
                })
        
        # Sort by match score
        detected_combinations.sort(key=lambda x: x["match_score"], reverse=True)
        
        # If no specific matches, provide intelligent defaults with RAG context
        if not detected_combinations:
            detected_combinations = self._get_default_combinations(story_analysis, rag_insights, requested_count)
        
        print(f"   Detected {len(detected_combinations)} matching combinations")
        return detected_combinations[:requested_count * 2]  # Return more for selection
    
    def determine_test_case_count(self, user_story: str, story_analysis: dict = None) -> int:
        """Intelligently determine the number of test cases needed based on story analysis"""
        story_lower = user_story.lower()
        
        if story_analysis is None:
            story_analysis = self._analyze_user_story(story_lower)
        
        # Full coverage indicators (31 test cases)
        full_coverage_keywords = [
            "comprehensive", "complete", "all scenarios", "full coverage", "entire workflow",
            "end-to-end", "all combinations", "thorough testing", "complete validation", 
            "all test cases", "complete test suite", "exhaustive", "full suite"
        ]
        
        # Association process indicators - these require comprehensive testing
        association_keywords = [
            "association process", "retrieve orders", "account to device", "partner account id",
            "eero cloud", "customer account", "device association", "process built", 
            "cable one to eero", "association", "comprehensive device testing"
        ]
        
        if any(keyword in story_lower for keyword in full_coverage_keywords):
            print(f"     -> Full coverage detected: comprehensive testing keywords found")
            return 31
            
        if any(keyword in story_lower for keyword in association_keywords):
            print(f"     -> Association process detected: requires comprehensive device lifecycle testing")
            return 31
        
        # Calculate base score from story characteristics
        complexity_score = 0
        
        # Customer type variety
        if len(story_analysis.get("customer_segments", [])) >= 2:
            complexity_score += 3  # Both RESI and BUSI
            print(f"     -> Both customer types detected (+3)")
        else:
            complexity_score += 1  # Single customer type
            print(f"     -> Single customer type detected (+1)")
        
        # Scenario type variety  
        if len(story_analysis.get("order_types", [])) >= 2:
            complexity_score += 3  # Both install and CoS
            print(f"     -> Both install and CoS scenarios detected (+3)")
        else:
            complexity_score += 1  # Single scenario type
            print(f"     -> Single scenario type detected (+1)")
        
        # Device lifecycle complexity
        if story_analysis.get("device_lifecycle_required", False):
            complexity_score += 4  # Device management/association processes
            print(f"     -> Device lifecycle management detected (+4)")
        
        if story_analysis.get("association_process_detected", False):
            complexity_score += 3  # Association processes need comprehensive coverage
            print(f"     -> Association process detected (+3)")
        
        # Eero type variety
        eero_types_count = len(set(story_analysis.get("eero_types", [])))
        if eero_types_count >= 4:
            complexity_score += 3  # Multiple eero types
            print(f"     -> Multiple eero types detected: {eero_types_count} (+3)")
        elif eero_types_count >= 2:
            complexity_score += 2  # Some variety
            print(f"     -> Some eero type variety detected: {eero_types_count} (+2)")
        else:
            complexity_score += 1  # Basic eero types
            print(f"     -> Basic eero types detected: {eero_types_count} (+1)")
        
        # Business criticality indicators
        critical_keywords = [
            "critical", "important", "priority", "business critical", "production",
            "essential", "mandatory", "required", "compliance", "validation"
        ]
        
        if any(keyword in story_lower for keyword in critical_keywords):
            complexity_score += 2
            print(f"     -> Business critical indicators detected (+2)")
        
        # Missing combination priority
        missing_combo_keywords = [
            "device removal", "remove device", "device lifecycle", "gateway removal",
            "service removal", "equipment removal"
        ]
        
        if any(keyword in story_lower for keyword in missing_combo_keywords):
            complexity_score += 2
            print(f"     -> Missing combination priority detected (+2)")
        
        print(f"     -> Total complexity score: {complexity_score}")
        
        # Map complexity score to test case count
        if complexity_score >= 15:
            return min(31, max(20, complexity_score))  # Very high complexity
        elif complexity_score >= 12:
            return min(15, max(10, complexity_score))  # High complexity  
        elif complexity_score >= 8:
            return min(12, max(6, complexity_score))   # Medium complexity
        elif complexity_score >= 5:
            return min(8, max(4, complexity_score))    # Low-medium complexity
        else:
            return max(3, complexity_score)            # Low complexity
    
    def _analyze_user_story(self, story: str) -> dict:
        """Extract key information from user story with device lifecycle intelligence"""
        analysis = {
            "order_types": [],
            "customer_segments": [],
            "truck_roll_preference": "both",
            "eero_types": [],
            "specific_scenarios": [],
            "device_lifecycle_required": False,
            "association_process_detected": False
        }
        
        # Detect order type - can be both
        if any(word in story for word in ["install", "new customer", "first time", "setup"]):
            analysis["order_types"].append("install")
        if any(word in story for word in ["change", "modify", "add", "remove", "upgrade", "existing", "cos"]):
            analysis["order_types"].append("cos")
        if not analysis["order_types"]:
            analysis["order_types"] = ["install", "cos"]  # both if unclear
        
        # Detect customer segments  
        if any(word in story for word in ["residential", "resi", "home"]):
            analysis["customer_segments"].append("residential")
        if any(word in story for word in ["business", "commercial", "busi"]):
            analysis["customer_segments"].append("business")
        if not analysis["customer_segments"]:
            analysis["customer_segments"] = ["residential", "business"]  # both
        
        # Detect truck roll preference
        if any(phrase in story for phrase in ["no truck", "self install", "without technician"]):
            analysis["truck_roll_preference"] = "no"
        elif any(phrase in story for phrase in ["truck roll", "technician", "installation visit"]):
            analysis["truck_roll_preference"] = "with"
        
        # Detect association and device lifecycle patterns
        association_keywords = ["association", "associate", "binding", "bind", "device management", "account-to-device", "partner account"]
        if any(keyword in story for keyword in association_keywords):
            analysis["association_process_detected"] = True
            analysis["device_lifecycle_required"] = True
            # Association processes require comprehensive device lifecycle testing
            analysis["specific_scenarios"].extend(["device_association", "device_removal", "lifecycle_management"])
        
        # Detect eero types
        if any(word in story for word in ["plus", "premium", "enhanced"]):
            analysis["eero_types"].extend(["eero_plus", "add_eero_plus"])
        if any(phrase in story for phrase in ["additional", "multiple", "mesh", "more than one"]):
            analysis["eero_types"].extend(["eero_additional", "add_additional"])
        if any(word in story for word in ["remove", "delete"]):
            analysis["eero_types"].extend(["remove_eero", "remove_device_not_gateway", "remove_device_gateway"])
        if any(word in story for word in ["basic", "standard"]) or not analysis["eero_types"]:
            analysis["eero_types"].extend(["eero", "add_eero"])
        
        # If association process detected, add removal scenarios for complete lifecycle testing
        if analysis["association_process_detected"]:
            analysis["eero_types"].extend([
                "remove_device_not_gateway", 
                "remove_device_gateway", 
                "remove_eero_along_device"
            ])
            # Ensure both residential and business scenarios for comprehensive coverage
            if not analysis["customer_segments"]:
                analysis["customer_segments"] = ["residential", "business"]
        
        return analysis
    
    def _get_rag_context_insights(self, user_story: str) -> dict:
        """Get insights from RAG context"""
        if not self.rag_context:
            return {}
        
        insights = {'relevant_contexts': [], 'business_purpose': ''}
        
        try:
            # Get combination intelligence from RAG
            combo_intel = self.rag_context.get_combination_intelligence(user_story)
            insights['detected_combination'] = combo_intel.get('detected_combination', 'base_eero')
            insights['workflow_type'] = combo_intel.get('workflow_type', 'standard_install')
            
            # Search for relevant contexts
            story_keywords = [word.lower() for word in user_story.split() 
                            if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that']]
            
            for keyword in story_keywords[:5]:
                relevant = self.rag_context.search_context(keyword)
                insights['relevant_contexts'].extend(relevant[:2])
            
        except Exception as e:
            print(f"   RAG context error: {e}")
        
        return insights
    
    def _calculate_match_score(self, combo: dict, analysis: dict, rag_insights: dict = None) -> float:
        """Calculate match score with device lifecycle intelligence"""
        score = 0.0
        
        # Order type match
        if combo["order_type"] in analysis["order_types"]:
            score += 0.25
        
        # Customer segment match
        if combo["segment"] in analysis["customer_segments"]:
            score += 0.25
        
        # Truck roll match
        if (analysis["truck_roll_preference"] == "both" or 
            combo["truck_roll"] == analysis["truck_roll_preference"]):
            score += 0.2
        
        # Eero type match
        if combo["eero_type"] in analysis["eero_types"]:
            score += 0.3
        elif any(eero_type in combo["eero_type"] for eero_type in analysis["eero_types"]):
            score += 0.15
        
        # Device lifecycle boost - prioritize removal scenarios for association stories
        if analysis.get("association_process_detected", False):
            if "remove" in combo["eero_type"]:
                score += 0.4  # Strong boost for removal scenarios when association detected
            elif combo["order_type"] == "cos":
                score += 0.2  # Boost for change of service scenarios
        
        # Business segment boost for device management stories
        if analysis.get("device_lifecycle_required", False) and combo["segment"] == "business":
            score += 0.15  # Business scenarios often more comprehensive for device management
        
        return score
    
    def _get_default_combinations(self, analysis: dict, rag_insights: dict, requested_count: int) -> list:
        """Get intelligent defaults"""
        defaults = []
        
        for order_type in analysis["order_types"]:
            for segment in analysis["customer_segments"]:
                for eero_type in ["eero", "eero_plus"][:2]:  # Basic defaults
                    combo = {
                        "combination": {
                            "id": 999,
                            "order_type": order_type,
                            "customer_status": "new" if order_type == "install" else "existing_hsd",
                            "segment": segment,
                            "truck_roll": "with",
                            "eero_type": eero_type,
                            "description": f"Default {order_type} {segment} {eero_type}"
                        },
                        "match_score": 0.5,
                        "service_code": self.service_code_mapping.get(eero_type, "HE008"),
                        "rag_context": ""
                    }
                    defaults.append(combo)
        
        return defaults[:requested_count]
    
    def get_combination_requirements(self, detected_combinations: list) -> list:
        """Convert detected combinations to TestCaseRequirement format with consolidation"""
        # Group combinations by requirement type to consolidate duplicates
        requirement_groups = {}
        
        for detection in detected_combinations:
            combo = detection["combination"]
            
            # Map to existing format
            customer_type = "RESI" if combo["segment"] == "residential" else "BUSI"
            scenario_type = combo["order_type"]
            truck_roll_type = "With" if combo["truck_roll"] == "with" else "No"
            
            # Create balanced grouping key - smart consolidation with critical ID preservation
            customer_status = combo.get("customer_status", "")
            eero_type = combo.get("eero_type", "")
            
            # Only create specific keys for critical IDs 29-31 to preserve their distinction
            if combo["id"] in [29, 30, 31]:
                # These critical device removal scenarios need unique identification
                scenario_map = {
                    "remove_device_not_gateway": "WithAdditionalEeroBusinessRemoveDeviceGatewayNo",
                    "remove_device_gateway": "WithAdditionalEeroBusinessRemoveDeviceGatewayYes", 
                    "remove_eero_along_device": "WithAdditionalEeroBusinessRemoveEeroServiceDevice",
                    "remove_eero_service_device": "WithAdditionalEeroBusinessRemoveEeroServiceDevice"
                }
                scenario_desc = scenario_map.get(eero_type, eero_type.replace("_", "").title())
                group_key = f"{customer_type}-{scenario_type}-{truck_roll_type}Truck-{scenario_desc}"
            else:
                # For all other scenarios, use standard consolidation
                group_key = f"{customer_type}-{scenario_type}-{truck_roll_type}Truck"
            
            if group_key not in requirement_groups:
                requirement_groups[group_key] = {
                    "customer_type": customer_type,
                    "scenario_type": scenario_type,
                    "truck_roll_type": truck_roll_type,
                    "count_needed": 0,
                    "priority": "high",
                    "combinations": []
                }
            
            # Add combination to group and increment count
            requirement_groups[group_key]["count_needed"] += 1
            requirement_groups[group_key]["combinations"].append({
                "combo": combo,
                "detection": detection
            })
        
        # Convert groups back to individual requirements with proper counts
        requirements = []
        for group_key, group_data in requirement_groups.items():
            req = TestCaseRequirement(
                customer_type=group_data["customer_type"],
                scenario_type=group_data["scenario_type"],
                truck_roll_type=group_data["truck_roll_type"],
                count_needed=group_data["count_needed"],
                priority=group_data["priority"],
                descriptive_name=group_key  # Preserve the descriptive group key
            )
            
            # Add metadata from the first combination in the group
            first_combo_data = group_data["combinations"][0]
            combo = first_combo_data["combo"]
            detection = first_combo_data["detection"]
            
            req.combination_id = combo["id"]
            req.eero_type = combo["eero_type"]
            req.service_code = detection["service_code"]
            req.customer_status = combo["customer_status"]
            req.description = f"Consolidated: {len(group_data['combinations'])} combinations for {group_key}"
            req.match_score = detection["match_score"]
            req.exact_combination_description = combo.get("description", "")  # Store exact combination description
            
            # Store all combinations for reference
            req.all_combinations = group_data["combinations"]
            
            requirements.append(req)
        
        print(f"   Requirement Consolidation: {len(detected_combinations)} combinations -> {len(requirements)} unique requirements")
        for group_key, group_data in requirement_groups.items():
            print(f"     {group_key}: need {group_data['count_needed']}")
        
        return requirements