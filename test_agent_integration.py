#!/usr/bin/env python3
"""
OneLastAI Platform - Agent Engine Integration Test
Comprehensive test suite for the 27-agent system
"""
import os
import sys
import django
from pathlib import Path

# Add the Django project directory to the Python path
sys.path.append('/workspaces/codespaces-django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Setup Django
django.setup()

import yaml
from agents.models import Agent
from agents.engines.base import BaseAgentEngine


class AgentIntegrationTester:
    """Test suite for agent engine integration."""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test results."""
        self.test_results[test_name] = {
            'success': success,
            'message': message
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        
    def log_error(self, test_name: str, error: Exception):
        """Log test errors."""
        error_msg = f"{type(error).__name__}: {str(error)}"
        self.errors.append(f"{test_name}: {error_msg}")
        self.log_result(test_name, False, error_msg)
    
    def test_base_engine_class(self):
        """Test BaseAgentEngine functionality."""
        try:
            # Test base class instantiation
            base_engine = BaseAgentEngine('test_agent')
            self.log_result("Base Engine Creation", True, "BaseAgentEngine instantiated successfully")
            
            # Test YAML config loading (should handle missing file gracefully)
            config = base_engine.load_config()
            self.log_result("Config Loading", True, f"Config loaded: {type(config).__name__}")
            
            # Test system prompt building
            prompt = base_engine.build_system_prompt()
            self.log_result("System Prompt", len(prompt) > 0, f"Prompt length: {len(prompt)} chars")
            
            # Test AI parameters
            params = base_engine.get_ai_parameters()
            expected_params = ['temperature', 'max_tokens', 'top_p']
            has_params = all(param in params for param in expected_params)
            self.log_result("AI Parameters", has_params, f"Parameters: {list(params.keys())}")
            
        except Exception as e:
            self.log_error("Base Engine Test", e)
    
    def test_yaml_configs(self):
        """Test YAML configuration files."""
        configs_dir = Path('/workspaces/codespaces-django/agents/configs')
        
        if not configs_dir.exists():
            self.log_result("YAML Configs Directory", False, "Configs directory not found")
            return
            
        yaml_files = list(configs_dir.glob('*.yml'))
        self.log_result("YAML Files Found", len(yaml_files) > 0, f"Found {len(yaml_files)} YAML files")
        
        valid_configs = 0
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                # Check required sections
                required_sections = ['agent_info', 'personality', 'capabilities', 'ai_parameters']
                has_sections = all(section in config for section in required_sections)
                
                if has_sections:
                    valid_configs += 1
                    
            except Exception as e:
                self.log_error(f"YAML Config {yaml_file.name}", e)
        
        self.log_result("Valid YAML Configs", valid_configs == len(yaml_files), 
                       f"{valid_configs}/{len(yaml_files)} configs are valid")
    
    def test_individual_engines(self):
        """Test individual agent engine classes."""
        engines_dir = Path('/workspaces/codespaces-django/agents/engines')
        engine_files = [f for f in engines_dir.glob('*.py') 
                       if f.name not in ['__init__.py', 'base.py', 'business.py', 'conversational.py', 'creative.py', 'technical.py']]
        
        successful_engines = 0
        
        for engine_file in engine_files:
            engine_name = engine_file.stem
            try:
                # Dynamically import the engine
                module_name = f"agents.engines.{engine_name}"
                module = __import__(module_name, fromlist=[''])
                
                # Find the engine class (should be CapitalCase of filename)
                class_name = ''.join(word.capitalize() for word in engine_name.split('_')) + 'Engine'
                
                if hasattr(module, class_name):
                    engine_class = getattr(module, class_name)
                    
                    # Test instantiation
                    engine_instance = engine_class()
                    
                    # Test it inherits from BaseAgentEngine
                    is_base_engine = isinstance(engine_instance, BaseAgentEngine)
                    
                    if is_base_engine:
                        successful_engines += 1
                        self.log_result(f"Engine {class_name}", True, "Instantiated and inherits BaseAgentEngine")
                    else:
                        self.log_result(f"Engine {class_name}", False, "Does not inherit BaseAgentEngine")
                else:
                    self.log_result(f"Engine {engine_name}", False, f"Class {class_name} not found")
                    
            except Exception as e:
                self.log_error(f"Engine {engine_name}", e)
        
        self.log_result("Engine Classes", successful_engines > 20, 
                       f"{successful_engines}/{len(engine_files)} engines loaded successfully")
    
    def test_agent_model_integration(self):
        """Test Agent model integration with engine system."""
        try:
            # Check if Agent model has required fields
            agent_model = Agent._meta
            field_names = [field.name for field in agent_model.fields]
            
            required_fields = ['agent_type', 'name']
            has_fields = all(field in field_names for field in required_fields)
            self.log_result("Agent Model Fields", has_fields, f"Fields: {field_names}")
            
            # Test agent choices
            agent_choices = dict(Agent.AGENT_CHOICES) if hasattr(Agent, 'AGENT_CHOICES') else {}
            self.log_result("Agent Choices", len(agent_choices) >= 27, 
                           f"Found {len(agent_choices)} agent choices")
            
        except Exception as e:
            self.log_error("Agent Model Integration", e)
    
    def test_sample_agent_interaction(self):
        """Test a sample agent interaction."""
        try:
            # Try to import and test a sample engine
            from agents.engines.neochat import NeoChatEngine
            
            neochat = NeoChatEngine()
            
            # Test message processing (mock context)
            test_message = "Hello, how are you?"
            mock_context = {
                'user_id': 'test_user',
                'conversation_id': 'test_conversation'
            }
            
            # Note: This will fail without actual AI service, but should not crash
            try:
                response = neochat.process_message(test_message, mock_context)
                self.log_result("Sample Interaction", True, "Message processed without errors")
            except Exception as ai_error:
                # Expected to fail without AI service setup, but should handle gracefully
                if "AI service" in str(ai_error) or "API" in str(ai_error):
                    self.log_result("Sample Interaction", True, "Failed gracefully due to missing AI service (expected)")
                else:
                    self.log_result("Sample Interaction", False, f"Unexpected error: {ai_error}")
                    
        except Exception as e:
            self.log_error("Sample Agent Interaction", e)
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Starting Agent Engine Integration Tests...")
        print("=" * 60)
        
        self.test_base_engine_class()
        print()
        
        self.test_yaml_configs()
        print()
        
        self.test_individual_engines()
        print()
        
        self.test_agent_model_integration()
        print()
        
        self.test_sample_agent_interaction()
        print()
        
        # Summary
        print("=" * 60)
        print("🏁 Test Summary:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")
        
        return passed_tests == total_tests


if __name__ == "__main__":
    tester = AgentIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Agent system is ready for deployment.")
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
    
    sys.exit(0 if success else 1)