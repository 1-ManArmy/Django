#!/usr/bin/env python3
"""
OneLastAI Platform - Simplified Agent Engine Integration Test
Basic test suite for the 27-agent system structure
"""
import os
import sys
import yaml
from pathlib import Path

# Add the Django project directory to the Python path
sys.path.append('/workspaces/codespaces-django')

class SimpleAgentTester:
    """Simplified test suite for agent engine integration."""
    
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
    
    def test_file_structure(self):
        """Test that all required files exist."""
        base_path = Path('/workspaces/codespaces-django')
        
        # Check base engine exists
        base_engine_path = base_path / 'agents' / 'engines' / 'base.py'
        self.log_result("Base Engine File", base_engine_path.exists(), 
                       f"File exists: {base_engine_path}")
        
        # Check engines directory structure
        engines_dir = base_path / 'agents' / 'engines'
        if engines_dir.exists():
            engine_files = [f for f in engines_dir.glob('*.py') 
                           if f.name not in ['__init__.py', 'base.py']]
            self.log_result("Engine Files", len(engine_files) >= 25, 
                           f"Found {len(engine_files)} engine files")
        else:
            self.log_result("Engines Directory", False, "Directory not found")
        
        # Check configs directory
        configs_dir = base_path / 'agents' / 'configs'
        if configs_dir.exists():
            yaml_files = list(configs_dir.glob('*.yml'))
            self.log_result("YAML Config Files", len(yaml_files) >= 25, 
                           f"Found {len(yaml_files)} YAML files")
        else:
            self.log_result("Configs Directory", False, "Directory not found")
    
    def test_yaml_configs(self):
        """Test YAML configuration files structure."""
        configs_dir = Path('/workspaces/codespaces-django/agents/configs')
        
        if not configs_dir.exists():
            self.log_result("YAML Configs Directory", False, "Configs directory not found")
            return
            
        yaml_files = list(configs_dir.glob('*.yml'))
        valid_configs = 0
        
        for yaml_file in yaml_files[:5]:  # Test first 5 files
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
        
        self.log_result("Sample YAML Configs", valid_configs > 0, 
                       f"{valid_configs}/5 sample configs are valid")
    
    def test_base_engine_syntax(self):
        """Test that base engine file has valid Python syntax."""
        try:
            base_engine_path = Path('/workspaces/codespaces-django/agents/engines/base.py')
            
            if not base_engine_path.exists():
                self.log_result("Base Engine Syntax", False, "File not found")
                return
                
            with open(base_engine_path, 'r') as f:
                code = f.read()
                
            # Try to compile the code
            compile(code, str(base_engine_path), 'exec')
            self.log_result("Base Engine Syntax", True, "Valid Python syntax")
            
            # Check for key class and methods
            has_class = 'class BaseAgentEngine' in code
            has_load_config = 'def load_config' in code
            has_process_message = 'def process_message' in code
            
            structure_ok = has_class and has_load_config and has_process_message
            self.log_result("Base Engine Structure", structure_ok, 
                           f"Class: {has_class}, load_config: {has_load_config}, process_message: {has_process_message}")
            
        except Exception as e:
            self.log_error("Base Engine Syntax", e)
    
    def test_sample_engine_syntax(self):
        """Test syntax of sample engine files."""
        engines_dir = Path('/workspaces/codespaces-django/agents/engines')
        
        if not engines_dir.exists():
            self.log_result("Sample Engine Syntax", False, "Engines directory not found")
            return
            
        engine_files = [f for f in engines_dir.glob('*.py') 
                       if f.name not in ['__init__.py', 'base.py']]
        
        valid_engines = 0
        
        for engine_file in engine_files[:3]:  # Test first 3 engines
            try:
                with open(engine_file, 'r') as f:
                    code = f.read()
                    
                # Try to compile the code
                compile(code, str(engine_file), 'exec')
                
                # Check for inheritance
                has_inheritance = 'BaseAgentEngine' in code
                has_class = 'class ' in code and 'Engine' in code
                
                if has_inheritance and has_class:
                    valid_engines += 1
                    
            except Exception as e:
                self.log_error(f"Engine {engine_file.name}", e)
        
        self.log_result("Sample Engine Syntax", valid_engines > 0, 
                       f"{valid_engines}/3 sample engines have valid syntax")
    
    def test_agent_model_file(self):
        """Test agents/models.py file structure."""
        try:
            models_path = Path('/workspaces/codespaces-django/agents/models.py')
            
            if not models_path.exists():
                self.log_result("Agent Models File", False, "File not found")
                return
                
            with open(models_path, 'r') as f:
                content = f.read()
                
            # Check for key components
            has_agent_choices = 'AGENT_CHOICES' in content
            has_agent_class = 'class Agent' in content
            has_django_import = 'from django.db import models' in content
            
            structure_ok = has_agent_choices and has_agent_class and has_django_import
            self.log_result("Agent Models Structure", structure_ok, 
                           f"AGENT_CHOICES: {has_agent_choices}, Agent class: {has_agent_class}")
            
            # Count agent choices
            if has_agent_choices:
                # Simple count of choices (approximate)
                choice_lines = [line for line in content.split('\n') if '(' in line and '),' in line and "'" in line]
                choice_count = len([line for line in choice_lines if line.strip().startswith('(')])
                self.log_result("Agent Choices Count", choice_count >= 25, 
                               f"Found approximately {choice_count} agent choices")
            
        except Exception as e:
            self.log_error("Agent Models File", e)
    
    def test_project_structure(self):
        """Test overall project structure."""
        base_path = Path('/workspaces/codespaces-django')
        
        # Check key directories
        key_dirs = [
            'agents', 'config', 'accounts', 'ai_services', 
            'api', 'core', 'dashboard'
        ]
        
        existing_dirs = []
        for dir_name in key_dirs:
            if (base_path / dir_name).exists():
                existing_dirs.append(dir_name)
        
        self.log_result("Project Structure", len(existing_dirs) >= 6, 
                       f"Found {len(existing_dirs)}/{len(key_dirs)} key directories: {existing_dirs}")
        
        # Check manage.py
        manage_py = base_path / 'manage.py'
        self.log_result("Django Project", manage_py.exists(), 
                       f"manage.py exists: {manage_py.exists()}")
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Starting Simplified Agent Engine Integration Tests...")
        print("=" * 70)
        
        self.test_project_structure()
        print()
        
        self.test_file_structure()
        print()
        
        self.test_agent_model_file()
        print()
        
        self.test_base_engine_syntax()
        print()
        
        self.test_sample_engine_syntax()
        print()
        
        self.test_yaml_configs()
        print()
        
        # Summary
        print("=" * 70)
        print("🏁 Test Summary:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(self.errors) > 3:
                print(f"  ... and {len(self.errors) - 3} more errors")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("\n🎉 Agent system structure looks good! Ready for Django integration.")
            return True
        else:
            print("\n⚠️  Some structural issues found. Please review the errors above.")
            return False


if __name__ == "__main__":
    tester = SimpleAgentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ Next steps: Django migrations and full integration testing")
    else:
        print("\n🔧 Fix structural issues before proceeding")
    
    sys.exit(0 if success else 1)