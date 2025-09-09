#!/usr/bin/env python
"""
Test script for the 27-Agent System
Tests engine loading, YAML configs, and agent functionality
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
django.setup()

def test_yaml_configs():
    """Test that all YAML configuration files exist and are valid"""
    print("🔍 Testing YAML Configuration Files...")
    
    configs_dir = BASE_DIR / 'agents' / 'configs'
    expected_agents = [
        'neochat', 'personax', 'girlfriend', 'emotisense', 'callghost', 'memora', 'socialwise',
        'configai', 'infoseek', 'documind', 'netscope', 'authwise', 'spylens',
        'codemaster', 'cinegen', 'contentcrafter', 'dreamweaver', 'ideaforge', 'aiblogster', 'vocamind', 'artisan',
        'datasphere', 'datavision', 'taskmaster', 'reportly', 'dnaforge', 'carebot'
    ]
    
    import yaml
    
    for agent in expected_agents:
        config_file = configs_dir / f'{agent}.yml'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Verify required sections
                required_sections = ['agent_info', 'personality', 'capabilities', 'ai_parameters', 'system_prompt']
                for section in required_sections:
                    assert section in config, f"Missing section '{section}' in {agent}.yml"
                
                print(f"   ✅ {agent}.yml - Valid configuration")
            except Exception as e:
                print(f"   ❌ {agent}.yml - Error: {e}")
                return False
        else:
            print(f"   ❌ {agent}.yml - File not found")
            return False
    
    print("   🎉 All YAML configurations are valid!")
    return True

def test_engine_classes():
    """Test that all engine classes exist and can be imported"""
    print("\n🔍 Testing Agent Engine Classes...")
    
    engines_dir = BASE_DIR / 'agents' / 'engines'
    expected_engines = [
        'neochat', 'personax', 'girlfriend', 'emotisense', 'callghost', 'memora', 'socialwise',
        'configai', 'infoseek', 'documind', 'netscope', 'authwise', 'spylens',
        'codemaster', 'cinegen', 'contentcrafter', 'dreamweaver', 'ideaforge', 'aiblogster', 'vocamind', 'artisan',
        'datasphere', 'datavision', 'taskmaster', 'reportly', 'dnaforge', 'carebot'
    ]
    
    for engine_name in expected_engines:
        try:
            # Import the engine module
            module_path = f'agents.engines.{engine_name}'
            module = __import__(module_path, fromlist=[''])
            
            # Get the engine class (assuming naming convention: EngineNameEngine)
            class_name = f"{engine_name.title()}Engine"
            if hasattr(module, class_name):
                engine_class = getattr(module, class_name)
                
                # Test instantiation
                engine_instance = engine_class()
                print(f"   ✅ {class_name} - Successfully imported and instantiated")
            else:
                print(f"   ❌ {class_name} - Class not found in module")
                return False
                
        except Exception as e:
            print(f"   ❌ {engine_name} - Error: {e}")
            return False
    
    print("   🎉 All engine classes imported successfully!")
    return True

def test_base_engine():
    """Test the BaseAgentEngine functionality"""
    print("\n🔍 Testing BaseAgentEngine...")
    
    try:
        from agents.engines.base import BaseAgentEngine
        
        # Test instantiation
        base_engine = BaseAgentEngine('test')
        print("   ✅ BaseAgentEngine instantiation")
        
        # Test YAML loading (using neochat as example)
        neochat_engine = BaseAgentEngine('neochat')
        config = neochat_engine.load_config()
        
        assert config is not None, "Config should not be None"
        assert 'agent_info' in config, "Config should have agent_info"
        print("   ✅ YAML configuration loading")
        
        # Test system prompt building
        system_prompt = neochat_engine.build_system_prompt()
        assert len(system_prompt) > 0, "System prompt should not be empty"
        print("   ✅ System prompt building")
        
        # Test AI parameters
        ai_params = neochat_engine.get_ai_parameters()
        assert 'temperature' in ai_params, "AI params should include temperature"
        print("   ✅ AI parameters retrieval")
        
        print("   🎉 BaseAgentEngine functionality verified!")
        return True
        
    except Exception as e:
        print(f"   ❌ BaseAgentEngine test failed: {e}")
        return False

def test_specific_engines():
    """Test specific engine functionality"""
    print("\n🔍 Testing Specific Engine Functionality...")
    
    test_engines = ['neochat', 'configai', 'codemaster', 'datasphere']
    
    for engine_name in test_engines:
        try:
            # Import and instantiate
            module_path = f'agents.engines.{engine_name}'
            module = __import__(module_path, fromlist=[''])
            class_name = f"{engine_name.title()}Engine"
            engine_class = getattr(module, class_name)
            engine = engine_class()
            
            # Test configuration loading
            config = engine.config
            assert config is not None, f"{engine_name} config should load"
            
            # Test system prompt
            prompt = engine.system_prompt
            assert len(prompt) > 0, f"{engine_name} should have system prompt"
            
            # Test validate_input method
            assert engine.validate_input("test message"), f"{engine_name} should validate input"
            assert not engine.validate_input(""), f"{engine_name} should reject empty input"
            
            print(f"   ✅ {class_name} - Functionality verified")
            
        except Exception as e:
            print(f"   ❌ {engine_name} - Error: {e}")
            return False
    
    print("   🎉 Specific engine functionality verified!")
    return True

def test_agent_model():
    """Test the Agent model with 27 agents"""
    print("\n🔍 Testing Agent Model...")
    
    try:
        from agents.models import Agent
        
        # Test that all 27 agents are defined
        agent_choices = dict(Agent.AGENT_CHOICES)
        expected_count = 27
        actual_count = len(agent_choices)
        
        assert actual_count == expected_count, f"Expected {expected_count} agents, found {actual_count}"
        print(f"   ✅ Agent model has all {expected_count} agents defined")
        
        # Test agent categories
        categories = {
            'Conversational': ['neochat', 'personax', 'girlfriend', 'emotisense', 'callghost', 'memora', 'socialwise'],
            'AI Services': ['configai', 'infoseek', 'documind', 'netscope', 'authwise', 'spylens'],
            'Creative & Content': ['codemaster', 'cinegen', 'contentcrafter', 'dreamweaver', 'ideaforge', 'aiblogster', 'vocamind', 'artisan'],
            'Business & Analytics': ['datasphere', 'datavision', 'taskmaster', 'reportly', 'dnaforge', 'carebot']
        }
        
        total_agents = sum(len(agents) for agents in categories.values())
        assert total_agents == 27, f"Category agents don't add up to 27: {total_agents}"
        
        for category, agents in categories.items():
            for agent in agents:
                assert agent in agent_choices, f"Agent '{agent}' not found in AGENT_CHOICES"
        
        print("   ✅ All agents properly categorized and defined")
        
        # Test model fields
        assert hasattr(Agent, 'engine_class'), "Agent model should have engine_class field"
        assert hasattr(Agent, 'config_file'), "Agent model should have config_file field"
        print("   ✅ Agent model fields verified")
        
        print("   🎉 Agent model verification complete!")
        return True
        
    except Exception as e:
        print(f"   ❌ Agent model test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting 27-Agent System Integration Tests")
    print("=" * 60)
    
    tests = [
        ("YAML Configuration Files", test_yaml_configs),
        ("Engine Class Imports", test_engine_classes),
        ("BaseAgentEngine Functionality", test_base_engine),
        ("Specific Engine Features", test_specific_engines),
        ("Agent Model Integration", test_agent_model)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Unexpected error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<10} {test_name}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The 27-Agent System is ready for production!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)