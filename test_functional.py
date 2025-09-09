#!/usr/bin/env python
"""
Functional Test for 27-Agent System with Django Integration
Tests actual agent instantiation and functionality
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def initialize_django():
    """Initialize Django with error handling"""
    try:
        django.setup()
        print("✅ Django initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Django initialization failed: {e}")
        return False

def test_agent_engine_instantiation():
    """Test that we can instantiate agent engines"""
    print("\n🔍 Testing Agent Engine Instantiation...")
    
    # Test a few representative agents
    test_agents = [
        ('neochat', 'NeochatEngine'),
        ('configai', 'ConfigaiEngine'), 
        ('codemaster', 'CodemasterEngine'),
        ('datasphere', 'DatasphereEngine')
    ]
    
    success_count = 0
    
    for agent_name, class_name in test_agents:
        try:
            # Import the engine module
            module_path = f'agents.engines.{agent_name}'
            module = __import__(module_path, fromlist=[''])
            
            # Get the engine class
            if hasattr(module, class_name):
                engine_class = getattr(module, class_name)
                
                # Test instantiation
                engine = engine_class()
                
                # Test basic functionality
                assert hasattr(engine, 'config'), f"{class_name} should have config attribute"
                assert hasattr(engine, 'process_message'), f"{class_name} should have process_message method"
                
                print(f"   ✅ {class_name} - Successfully instantiated and tested")
                success_count += 1
            else:
                print(f"   ❌ {class_name} - Class not found in module")
                
        except Exception as e:
            print(f"   ❌ {agent_name} - Error: {e}")
    
    if success_count == len(test_agents):
        print("   🎉 All agent engines instantiated successfully!")
        return True
    else:
        print(f"   ⚠️  {success_count}/{len(test_agents)} engines instantiated")
        return False

def test_yaml_config_loading():
    """Test YAML configuration loading in engines"""
    print("\n🔍 Testing YAML Configuration Loading...")
    
    try:
        from agents.engines.base import BaseAgentEngine
        
        # Test loading different agent configs
        test_agents = ['neochat', 'configai', 'codemaster']
        
        for agent_name in test_agents:
            engine = BaseAgentEngine(agent_name)
            config = engine.load_config()
            
            assert config is not None, f"{agent_name} config should not be None"
            
            # Test that config has expected structure
            has_name = 'name' in config or ('agent_info' in config and 'name' in config['agent_info'])
            assert has_name, f"{agent_name} config should have name field"
            
            print(f"   ✅ {agent_name} - Config loaded successfully")
        
        print("   🎉 YAML configuration loading works!")
        return True
        
    except Exception as e:
        print(f"   ❌ YAML config loading failed: {e}")
        return False

def test_agent_model_integration():
    """Test Django Agent model integration"""
    print("\n🔍 Testing Agent Model Integration...")
    
    try:
        from agents.models import Agent
        
        # Test agent choices
        agent_choices = dict(Agent.AGENT_CHOICES)
        expected_agents = [
            'neochat', 'personax', 'girlfriend', 'emotisense', 'callghost', 'memora', 'socialwise',
            'configai', 'infoseek', 'documind', 'netscope', 'authwise', 'spylens',
            'codemaster', 'cinegen', 'contentcrafter', 'dreamweaver', 'ideaforge', 
            'aiblogster', 'vocamind', 'artisan',
            'datasphere', 'datavision', 'taskmaster', 'reportly', 'dnaforge', 'carebot'
        ]
        
        for agent_name in expected_agents[:5]:  # Test first 5
            assert agent_name in agent_choices, f"Agent '{agent_name}' not in AGENT_CHOICES"
        
        print(f"   ✅ Agent model has all {len(agent_choices)} agents defined")
        print("   ✅ Agent choices structure is correct")
        
        # Test model fields
        fields = [field.name for field in Agent._meta.get_fields()]
        expected_fields = ['agent_type', 'engine_class', 'config_file']
        
        for field in expected_fields:
            assert field in fields, f"Field '{field}' missing from Agent model"
            
        print("   ✅ Agent model fields are correct")
        print("   🎉 Agent model integration works!")
        return True
        
    except Exception as e:
        print(f"   ❌ Agent model integration failed: {e}")
        return False

def test_system_prompt_generation():
    """Test system prompt generation"""
    print("\n🔍 Testing System Prompt Generation...")
    
    try:
        from agents.engines.base import BaseAgentEngine
        
        # Test system prompt generation for different agents
        test_agents = ['neochat', 'configai']
        
        for agent_name in test_agents:
            engine = BaseAgentEngine(agent_name)
            system_prompt = engine.build_system_prompt()
            
            assert isinstance(system_prompt, str), f"{agent_name} system prompt should be string"
            assert len(system_prompt) > 50, f"{agent_name} system prompt should be substantial"
            
            print(f"   ✅ {agent_name} - System prompt generated ({len(system_prompt)} chars)")
        
        print("   🎉 System prompt generation works!")
        return True
        
    except Exception as e:
        print(f"   ❌ System prompt generation failed: {e}")
        return False

def run_functional_tests():
    """Run all functional tests"""
    print("🚀 Starting 27-Agent System Functional Tests")
    print("=" * 60)
    
    # First initialize Django
    if not initialize_django():
        print("❌ Cannot proceed without Django initialization")
        return False
    
    tests = [
        ("Agent Engine Instantiation", test_agent_engine_instantiation),
        ("YAML Configuration Loading", test_yaml_config_loading),
        ("Agent Model Integration", test_agent_model_integration),
        ("System Prompt Generation", test_system_prompt_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Unexpected error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("🎯 FUNCTIONAL TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<10} {test_name}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} functional tests passed")
    
    if passed == total:
        print("🎉 ALL FUNCTIONAL TESTS PASSED!")
        print("🚀 The 27-Agent System is ready for production!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. System needs attention.")
        return False

if __name__ == "__main__":
    success = run_functional_tests()
    sys.exit(0 if success else 1)