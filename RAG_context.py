"""
RAG Context for Test Case Generation
Generated automatically from test case files
Contains contextual information about each test case for improved LLM understanding
"""

class TestCaseRAGContext:
    def __init__(self):
        self.chunks = [
            {
                        "file_name": "BUSI - CoS - Customer having Eero service adding additional Eero device.txt",
                        "context_summary": "Complete business CoS workflow for adding additional eero devices to existing business customers",
                        "business_purpose": "Validates complete workflow: existing customer → service modification → additional device provisioning → integration validation",
                        "workflow_phases": "Service Provisioning → Technical Execution → Integration Validation (skips customer setup)",
                        "combination_intelligence": "BUSI CoS add_additional eero device with equipment management workflow",
                        "service_codes": ["HE008", "additional device management"],
                        "validation_requirements": "Kafka eero-order verification, banhammer device config, eero provisioning API, mesh network validation",
                        "workflow_complexity": "Medium - existing customer service modification with device addition",
                        "step_count_range": "18-22 steps typical for CoS with device addition",
                        "critical_phases": ["Service modification", "Equipment validation", "Mesh network setup", "Integration validation"],
                        "keywords": [
                                    "business",
                                    "change_of_service", 
                                    "additional_device",
                                    "equipment_management",
                                    "mesh_network",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "business",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a commercial test customer with an active Internet Plan & Eero W2W service along with\nan active HSD device & active Eero device;\n- an Eero device is ready to use for the test accoun..."
            },
            {
                        "file_name": "BUSI - CoS - Customer having Eero service removing addiitonal Eero device (Gateway No).txt",
                        "context_summary": "Test case for change_of_service involving business services",
                        "business_purpose": "Ensures change_of_service work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "business",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a commercial test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a t..."
            },
            {
                        "file_name": "BUSI - CoS - Customer having Eero service removing additional Eero device (Gateway Yes).txt",
                        "context_summary": "Test case for change_of_service involving business services",
                        "business_purpose": "Ensures change_of_service work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "business",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a commercial test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a t..."
            },
            {
                        "file_name": "BUSI - CoS - Customer having Eero Service with additional Eero device removing Eero Service.txt",
                        "context_summary": "Test case for change_of_service involving business services",
                        "business_purpose": "Ensures change_of_service work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "business",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a commercial test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a t..."
            },
            {
                        "file_name": "BUSI - CoS Customer adding Eero Service.txt",
                        "context_summary": "Test case for change_of_service involving business services",
                        "business_purpose": "Ensures change_of_service work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "business",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisites:\n- a commercial test customer with an active Internet Plan along with active HSD device;\n- an Eero device is ready to use for the test account.\nMake sure that the customer's phone num..."
            },
            {
                        "file_name": "BUSI - Install HSD along with Eero - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving business services",
                        "business_purpose": "Ensures installation work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "business",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nAn HSD device and an Eero device in ACSR are ready to be installed.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncustomer in the \"eero..."
            },
            {
                        "file_name": "BUSI - Install HSD along with Eero - With TruckRoll.txt",
                        "context_summary": "Test case for installation involving business services",
                        "business_purpose": "Ensures installation work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "business",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes an HSD and Eero devices, both in ACSR and ETA Direct.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncu..."
            },
            {
                        "file_name": "BUSI - Install HSD along with Eero More than 1 Eero Device - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving business services",
                        "business_purpose": "Ensures installation work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "business",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nAn HSD device and multiple Eero devices in ACSR are ready to be installed.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncustomer in th..."
            },
            {
                        "file_name": "BUSI - Install HSD along with Eero More than 1 Eero Device - With TruckRoll.txt",
                        "context_summary": "Test case for installation involving business services",
                        "business_purpose": "Ensures installation work correctly for business segment",
                        "keywords": [
                                    "business",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "business",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes an HSD device and Eero devices in ACSR and ETA Direct.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\nc..."
            },
            {
                        "file_name": "RESI - CoS - Customer adding Eero Service - No Truck Roll.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisites:\n- a residential test customer with an active Internet Plan along with active HSD device;\n- an Eero device is ready to use for the test account.\nMake sure that the customer's phone nu..."
            },
            {
                        "file_name": "RESI - CoS - Customer adding Eero Service - With Truck Roll.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisites:\n- a residential test customer with an active Internet Plan along with active HSD device;\n- an Eero device is ready to use for the test account both in ACSR & ETA.Make sure that the\nc..."
            },
            {
                        "file_name": "RESI - CoS - Customer having Eero service  removing additional Eero device (Gateway No).txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a ..."
            },
            {
                        "file_name": "RESI - CoS - Customer having Eero service adding additional Eero device.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan & Eero W2W service along with an\nactive HSD device & active Eero device;\n- an Eero device is ready to use for the test accou..."
            },
            {
                        "file_name": "RESI - CoS - Customer having Eero service removing additional Eero device (Gateway Yes).txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a ..."
            },
            {
                        "file_name": "RESI - CoS - Customer having Eero Service with additional Eero device removing Eero Service.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan, active Eero W2W, Eero additional\nservice along with active HSD device & two active Eero devices.\n- the test customer has a ..."
            },
            {
                        "file_name": "RESI - Install HSD along with Eero - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite: An HSD device and an Eero device in ACSR are ready to be installed.Make sure\nthat the customer's phone number is not in eero Insight. If it is there, delete the customer in the\n\"eero ..."
            },
            {
                        "file_name": "RESI - Install HSD along with Eero - With TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes an HSD device and an Eero device, both in ACSR and ETA\nDirect.\nMake sure that the customer's phone number is not in eero Insight. If it is there, dele..."
            },
            {
                        "file_name": "RESI - Install HSD along with Eero More than 1 Eero Device - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nAn HSD device and multiple Eero devices in ACSR are ready to be installed.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncustomer in th..."
            },
            {
                        "file_name": "RESI - Install HSD along with Eero More than 1 Eero Device - With TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes HSD and Eero devices in ACSR and ETA Direct.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncustomer in..."
            },
            {
                        "file_name": "[PLUS] RESI - CoS - Customer having Eero Plus adding additional Eero device.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan & active Eero W2W, Eero Secure\nPlus services along with an active HSD device & active Eero device;\n- an Eero device is ready..."
            },
            {
                        "file_name": "[PLUS] RESI - CoS - Customer having Eero Plus changing to Eero Service.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\nA residential test customer with an active Internet Plan & Eero W2W w/ Eero Secure Plus\nservice along with an active HSD device & active Eero device.\n2.\nOn the ACSR Common Search wind..."
            },
            {
                        "file_name": "[PLUS] RESI - CoS - Customer having Eero Plus removing additional Eero device.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan, active Eero W2W, Eero Secure\nPlus, Eero additional service along with active HSD device & two active Eero devices.\n2.\nOn th..."
            },
            {
                        "file_name": "[PLUS] RESI - CoS - Customer having Eero Secure Plus with additional Eero device removing Eero Service.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\n- a residential test customer with an active Internet Plan, active Eero W2W, Eero Secure\nPlus, Eero additional service along with active HSD device & two active Eero devices.\n2.\nOn th..."
            },
            {
                        "file_name": "[PLUS] RESI - CoS - Customer having Eero Service changing to Eero Plus.txt",
                        "context_summary": "Test case for change_of_service involving residential services",
                        "business_purpose": "Ensures change_of_service work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "change_of_service",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "change_of_service",
                        "customer_segment": "residential",
                        "primary_scenario": "change_of_service validation",
                        "content_preview": "1.\nPrerequisite:\nA residential test customer with an active Internet Plan & active Eero W2W service, along\nwith an active HSD device & active Eero device.\n2.\nOn the ACSR Common Search window:\n- enter ..."
            },
            {
                        "file_name": "[PLUS] RESI - Install HSD along with Eero Secure Plus - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nAn HSD device and an Eero device in ACSR are ready to be installed.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the customer in\nthe \"eero..."
            },
            {
                        "file_name": "[PLUS] RESI - Install HSD along with Eero Secure Plus - with TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes an HSD device and an Eero device, both in ACSR and ETA\nDirect.\nMake sure that the customer's phone number is not in eero Insight. If it is there, dele..."
            },
            {
                        "file_name": "[PLUS] RESI - Install HSD along with Eero Secure Plus More than 1 Eero Device - No TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite: An HSD device and multiple Eero devices in ACSR are ready to be installed.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the customer in\nth..."
            },
            {
                        "file_name": "[PLUS] RESI - Install HSD along with Eero Secure Plus More than 1 Eero Device - With TruckRoll.txt",
                        "context_summary": "Test case for installation involving residential services",
                        "business_purpose": "Ensures installation work correctly for residential segment",
                        "keywords": [
                                    "residential",
                                    "installation",
                                    "validation",
                                    "automation"
                        ],
                        "test_category": "installation",
                        "customer_segment": "residential",
                        "primary_scenario": "installation validation",
                        "content_preview": "1.\nPrerequisite:\nThe test tech inventory includes HSD and Eero devices in ACSR and ETA Direct.\nMake sure that the customer's phone number is not in eero Insight. If it is there, delete the\ncustomer in..."
            }
]



# Add comprehensive combination intelligence
        self.combination_intelligence = {
            "eero_products": {
                "base_eero": {
                    "service_codes": ["HE008", "EERO_BASIC"],
                    "description": "Standard Eero Wi-Fi service",
                    "features": ["basic_wifi", "single_device"],
                    "api_endpoints": ["/eero/basic/associate", "/eero/device/setup"],
                    "validation_points": ["device_association", "basic_connectivity"]
                },
                "eero_plus": {
                    "service_codes": ["HE009", "EERO_PLUS"],
                    "description": "Eero Plus with enhanced features",
                    "features": ["advanced_wifi", "security_features", "parental_controls"],
                    "api_endpoints": ["/eero/plus/associate", "/eero/plus/security/setup"],
                    "validation_points": ["enhanced_association", "security_validation", "premium_features"]
                },
                "eero_secure": {
                    "service_codes": ["HE010", "EERO_SECURE"],
                    "description": "Eero Secure with premium security",
                    "features": ["premium_security", "threat_protection", "advanced_controls"],
                    "api_endpoints": ["/eero/secure/associate", "/eero/security/configure"],
                    "validation_points": ["security_association", "threat_protection_setup", "advanced_validation"]
                },
                "multiple_devices": {
                    "service_codes": ["HE008_MULTI", "EERO_ADDITIONAL"],
                    "description": "Multiple Eero devices configuration",
                    "features": ["multi_device", "mesh_network", "device_management"],
                    "api_endpoints": ["/eero/devices/bulk-associate", "/eero/mesh/configure"],
                    "validation_points": ["multi_device_association", "mesh_validation", "device_management"]
                }
            },
            "combination_patterns": {
                "install_combinations": {
                    "new_base_install": {
                        "trigger_keywords": ["new customer", "first time", "basic installation"],
                        "product_type": "base_eero",
                        "workflow_type": "standard_install",
                        "key_modifications": {
                            "service_codes": "HE008",
                            "api_calls": "basic_association_flow",
                            "validation": "standard_connectivity_check"
                        }
                    },
                    "new_premium_install": {
                        "trigger_keywords": ["plus", "secure", "premium", "enhanced"],
                        "product_type": "eero_plus",
                        "workflow_type": "premium_install",
                        "key_modifications": {
                            "service_codes": "HE009",
                            "api_calls": "premium_association_flow",
                            "validation": "enhanced_security_validation"
                        }
                    },
                    "multi_device_install": {
                        "trigger_keywords": ["multiple", "additional devices", "mesh"],
                        "product_type": "multiple_devices",
                        "workflow_type": "multi_device_install",
                        "key_modifications": {
                            "service_codes": "HE008_MULTI",
                            "api_calls": "bulk_device_association",
                            "validation": "mesh_network_validation"
                        }
                    }
                },
                "cos_combinations": {
                    "add_premium_service": {
                        "trigger_keywords": ["upgrade", "add plus", "add secure"],
                        "product_type": "eero_plus",
                        "workflow_type": "service_upgrade",
                        "key_modifications": {
                            "service_codes": "upgrade_to_HE009",
                            "api_calls": "service_modification_flow",
                            "validation": "premium_feature_activation"
                        }
                    },
                    "add_additional_device": {
                        "trigger_keywords": ["add device", "additional eero", "expand network"],
                        "product_type": "multiple_devices",
                        "workflow_type": "device_addition",
                        "key_modifications": {
                            "service_codes": "add_HE008_device",
                            "api_calls": "device_addition_flow",
                            "validation": "new_device_mesh_integration"
                        }
                    },
                    "remove_device": {
                        "trigger_keywords": ["remove device", "delete eero", "reduce devices"],
                        "product_type": "device_removal",
                        "workflow_type": "device_removal",
                        "key_modifications": {
                            "service_codes": "remove_device_service",
                            "api_calls": "device_deactivation_flow",
                            "validation": "network_reconfiguration_check"
                        }
                    }
                }
            },
            "template_modification_rules": {
                "service_code_replacements": {
                    "base_to_plus": {"HE008": "HE009", "EERO_BASIC": "EERO_PLUS"},
                    "base_to_secure": {"HE008": "HE010", "EERO_BASIC": "EERO_SECURE"},
                    "single_to_multi": {"HE008": "HE008_MULTI", "device": "devices"}
                },
                "api_endpoint_modifications": {
                    "premium_upgrade": {
                        "replace": {"/eero/basic/": "/eero/plus/"},
                        "add_steps": ["security_feature_validation", "premium_subscription_check"]
                    },
                    "multi_device": {
                        "replace": {"/eero/device/": "/eero/devices/bulk-"},
                        "add_steps": ["mesh_network_setup", "device_sync_validation"]
                    }
                },
                "validation_step_enhancements": {
                    "plus_secure_validations": [
                        "Verify premium subscription activation",
                        "Validate security features are enabled",
                        "Check parental control accessibility"
                    ],
                    "multi_device_validations": [
                        "Verify all devices appear in mesh network",
                        "Validate device communication between nodes",
                        "Check network coverage optimization"
                    ]
                }
            }
        }
    
    def get_combination_intelligence(self, user_story: str) -> dict:
        """Analyze user story and return specific combination intelligence"""
        story_lower = user_story.lower()
        
        # Detect combination type
        detected_combination = "base_eero"  # default
        
        if any(keyword in story_lower for keyword in ["plus", "secure", "premium", "enhanced"]):
            detected_combination = "eero_plus"
        elif any(keyword in story_lower for keyword in ["multiple", "additional", "mesh", "more than one"]):
            detected_combination = "multiple_devices"
        
        # Detect workflow type
        workflow_type = "standard_install"
        if any(keyword in story_lower for keyword in ["upgrade", "add", "change", "modify"]):
            workflow_type = "service_upgrade"
        elif any(keyword in story_lower for keyword in ["remove", "delete", "reduce"]):
            workflow_type = "device_removal"
        
        combination_data = self.combination_intelligence["eero_products"].get(detected_combination, {})
        
        return {
            "detected_combination": detected_combination,
            "workflow_type": workflow_type,
            "product_info": combination_data,
            "modification_rules": self._get_modification_rules(detected_combination, workflow_type),
            "specific_adaptations": self._get_specific_adaptations(detected_combination, story_lower)
        }
    
    def _get_modification_rules(self, combination: str, workflow: str) -> dict:
        """Get specific modification rules for template adaptation"""
        rules = self.combination_intelligence["template_modification_rules"]
        
        modifications = {
            "service_codes": {},
            "api_endpoints": {},
            "validation_steps": []
        }
        
        if combination == "eero_plus":
            modifications["service_codes"] = rules["service_code_replacements"]["base_to_plus"]
            modifications["api_endpoints"] = rules["api_endpoint_modifications"]["premium_upgrade"]
            modifications["validation_steps"] = rules["validation_step_enhancements"]["plus_secure_validations"]
        elif combination == "multiple_devices":
            modifications["service_codes"] = rules["service_code_replacements"]["single_to_multi"]
            modifications["api_endpoints"] = rules["api_endpoint_modifications"]["multi_device"]
            modifications["validation_steps"] = rules["validation_step_enhancements"]["multi_device_validations"]
        
        return modifications
    
    def _get_specific_adaptations(self, combination: str, story_text: str) -> list:
        """Get specific adaptations needed based on combination and story"""
        adaptations = []
        
        if combination == "eero_plus":
            adaptations.extend([
                "Replace all instances of 'HE008' with 'HE009'",
                "Add security feature validation steps",
                "Include premium subscription verification",
                "Modify API endpoints to use /eero/plus/ instead of /eero/basic/"
            ])
        
        if combination == "multiple_devices":
            adaptations.extend([
                "Change single device references to multiple devices",
                "Add mesh network configuration steps",
                "Include device synchronization validation",
                "Modify API calls to use bulk operations"
            ])
        
        if "association process" in story_text:
            adaptations.append("Focus on account-to-device association workflow")
        
        if "new customer" in story_text:
            adaptations.append("Include new account creation steps")
        
        return adaptations

    # Keep existing methods
    def get_context_by_keywords(self, keywords: list) -> list:
        """Get relevant test case contexts based on keywords"""
        relevant_chunks = []
        for chunk in self.chunks:
            chunk_keywords = [kw.lower() for kw in chunk["keywords"]]
            if any(keyword.lower() in chunk_keywords for keyword in keywords):
                relevant_chunks.append(chunk)
        return relevant_chunks
    
    def get_context_by_category(self, category: str) -> list:
        """Get test case contexts by category"""
        return [chunk for chunk in self.chunks if chunk["test_category"].lower() == category.lower()]
    
    def get_context_by_customer_segment(self, segment: str) -> list:
        """Get test case contexts by customer segment"""
        return [chunk for chunk in self.chunks if chunk["customer_segment"].lower() == segment.lower()]
    
    def search_context(self, search_term: str) -> list:
        """Search for test cases containing specific terms"""
        search_term = search_term.lower()
        relevant_chunks = []
        for chunk in self.chunks:
            if (search_term in chunk["context_summary"].lower() or 
                search_term in chunk["business_purpose"].lower() or
                search_term in chunk["file_name"].lower() or
                any(search_term in keyword.lower() for keyword in chunk["keywords"])):
                relevant_chunks.append(chunk)
        return relevant_chunks
    
    def get_all_categories(self) -> list:
        """Get all unique test categories"""
        return list(set(chunk["test_category"] for chunk in self.chunks))
    
    def get_all_customer_segments(self) -> list:
        """Get all unique customer segments"""
        return list(set(chunk["customer_segment"] for chunk in self.chunks))
    
    def get_workflow_context(self, user_story: str) -> dict:
        """Get workflow-specific context for better test case generation"""
        story_lower = user_story.lower()
        
        workflow_context = {
            "detected_workflow": "install",  # default
            "expected_phases": [],
            "step_count_guidance": "20-25 steps",
            "critical_validations": [],
            "service_codes": ["HE008"]
        }
        
        # Detect workflow type
        if any(word in story_lower for word in ["change", "cos", "existing", "modify", "add", "remove"]):
            workflow_context["detected_workflow"] = "cos"
            workflow_context["expected_phases"] = ["Service Provisioning", "Technical Execution", "Integration Validation"]
            workflow_context["step_count_guidance"] = "18-22 steps"
        else:
            workflow_context["expected_phases"] = ["Customer Setup", "Service Provisioning", "Technical Execution", "Integration Validation"]
            workflow_context["step_count_guidance"] = "20-25 steps"
        
        # Detect service complexity
        if any(word in story_lower for word in ["plus", "premium", "secure", "enhanced"]):
            workflow_context["service_codes"].append("HE009")
            workflow_context["critical_validations"].append("Enhanced security features validation")
        
        if any(word in story_lower for word in ["multiple", "additional", "mesh", "device"]):
            workflow_context["step_count_guidance"] = "22-27 steps"
            workflow_context["critical_validations"].append("Multi-device mesh network validation")
        
        # Standard validations
        workflow_context["critical_validations"].extend([
            "Kafka eero-order queue verification",
            "Banhammer LDAP device configuration",
            "Eero provisioning API validation",
            "Eero Insight network creation"
        ])
        
        return workflow_context

# Create global instance for easy import
rag_context = TestCaseRAGContext()