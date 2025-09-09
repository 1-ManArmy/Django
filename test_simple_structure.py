#!/usr/bin/env python
"""
Simple Test Script for 27-Agent System Files
Tests file existence and basic YAML parsing without Django
"""
import os
import yaml
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("🔍 Testing File Structure...")
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # Test engine files
    engines_dir = BASE_DIR / 'agents' / 'engines'
    expected_engines = [
        'base.py', 'neochat.py', 'personax.py', 'girlfriend.py', 'emotisense.py', 'callghost.py', 'memora.py', 'socialwise.py',
        'configai.py', 'infoseek.py', 'documind.py', 'netscope.py', 'authwise.py', 'spylens.py',
        'codemaster.py', 'cinegen.py', 'contentcrafter.py', 'dreamweaver.py', 'ideaforge.py', 'aiblogster.py', 'vocamind.py', 'artisan.py',
        'datasphere.py', 'datavision.py', 'taskmaster.py', 'reportly.py', 'dnaforge.py', 'carebot.py'
    ]
    
    missing_engines = []
    for engine_file in expected_engines:
        engine_path = engines_dir / engine_file
        if not engine_path.exists():
            missing_engines.append(engine_file)
        else:
            print(f"   ✅ {engine_file}")
    
    if missing_engines:
        print(f"   ❌ Missing engine files: {missing_engines}")
        return False
    
    # Test config files
    configs_dir = BASE_DIR / 'agents' / 'configs'
    expected_configs = [
        'neochat.yml', 'personax.yml', 'girlfriend.yml', 'emotisense.yml', 'callghost.yml', 'memora.yml', 'socialwise.yml',
        'configai.yml', 'infoseek.yml', 'documind.yml', 'netscope.yml', 'authwise.yml', 'spylens.yml',
        'codemaster.yml', 'cinegen.yml', 'contentcrafter.yml', 'dreamweaver.yml', 'ideaforge.yml', 'aiblogster.yml', 'vocamind.yml', 'artisan.yml',
        'datasphere.yml', 'datavision.yml', 'taskmaster.yml', 'reportly.yml', 'dnaforge.yml', 'carebot.yml'
    ]
    
    missing_configs = []
    for config_file in expected_configs:
        config_path = configs_dir / config_file
        if not config_path.exists():
            missing_configs.append(config_file)
        else:
            print(f"   ✅ {config_file}")
    
    if missing_configs:
        print(f"   ❌ Missing config files: {missing_configs}")
        return False
    
    print("   🎉 All files exist!")
    return True

def test_yaml_parsing():
    """Test YAML file parsing"""
    print("\n🔍 Testing YAML File Parsing...")
    
    BASE_DIR = Path(__file__).resolve().parent
    configs_dir = BASE_DIR / 'agents' / 'configs'
    
    # Test a few sample configs
    test_configs = ['neochat.yml', 'configai.yml', 'codemaster.yml', 'datasphere.yml']
    
    for config_file in test_configs:
        config_path = configs_dir / config_file
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Verify required sections (flexible for both old and new structure)
            required_sections = ['personality', 'capabilities']
            missing_sections = []
            
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"   ❌ {config_file} - Missing sections: {missing_sections}")
                return False
            
            # Check name field (either top-level 'name' or in 'agent_info')
            has_name = False
            if 'name' in config and isinstance(config['name'], str):
                has_name = True
            elif 'agent_info' in config and 'name' in config['agent_info']:
                has_name = True
            
            if not has_name:
                print(f"   ❌ {config_file} - Missing name field")
                return False
            
            # Check temperature (either in 'parameters' or 'ai_parameters')
            has_temperature = False
            if 'parameters' in config and 'temperature' in config['parameters']:
                has_temperature = True
            elif 'ai_parameters' in config and 'temperature' in config['ai_parameters']:
                has_temperature = True
            
            if not has_temperature:
                print(f"   ❌ {config_file} - Missing temperature parameter")
                return False
            
            print(f"   ✅ {config_file} - Valid YAML structure")
            
        except Exception as e:
            print(f"   ❌ {config_file} - YAML parsing error: {e}")
            return False
    
    print("   🎉 YAML parsing successful!")
    return True

def test_engine_syntax():
    """Test basic Python syntax in engine files"""
    print("\n🔍 Testing Engine File Syntax...")
    
    BASE_DIR = Path(__file__).resolve().parent
    engines_dir = BASE_DIR / 'agents' / 'engines'
    
    # Test a few sample engines
    test_engines = ['base.py', 'neochat.py', 'configai.py', 'codemaster.py', 'datasphere.py']
    
    for engine_file in test_engines:
        engine_path = engines_dir / engine_file
        try:
            with open(engine_path, 'r') as f:
                content = f.read()
            
            # Basic syntax check by compiling
            compile(content, engine_file, 'exec')
            print(f"   ✅ {engine_file} - Valid Python syntax")
            
        except SyntaxError as e:
            print(f"   ❌ {engine_file} - Syntax error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ {engine_file} - Error: {e}")
            return False
    
    print("   🎉 Engine syntax validation passed!")
    return True

def test_agent_count():
    """Verify we have exactly 27 agents"""
    print("\n🔍 Testing Agent Count...")
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # Count engine files (excluding base.py and __init__.py)
    engines_dir = BASE_DIR / 'agents' / 'engines'
    engine_files = [f for f in engines_dir.glob('*.py') if f.name not in ['base.py', '__init__.py']]
    
    # Count config files
    configs_dir = BASE_DIR / 'agents' / 'configs'
    config_files = list(configs_dir.glob('*.yml'))
    
    expected_count = 27
    
    if len(engine_files) != expected_count:
        print(f"   ❌ Expected {expected_count} engine files, found {len(engine_files)}")
        return False
    
    if len(config_files) != expected_count:
        print(f"   ❌ Expected {expected_count} config files, found {len(config_files)}")
        return False
    
    print(f"   ✅ Correct count: {expected_count} engines and {expected_count} configs")
    
    # Verify matching names
    engine_names = {f.stem for f in engine_files}
    config_names = {f.stem for f in config_files}
    
    if engine_names != config_names:
        missing_engines = config_names - engine_names
        missing_configs = engine_names - config_names
        
        if missing_engines:
            print(f"   ❌ Missing engines for configs: {missing_engines}")
        if missing_configs:
            print(f"   ❌ Missing configs for engines: {missing_configs}")
        
        return False
    
    print("   ✅ All agents have matching engine and config files")
    print("   🎉 Agent count verification passed!")
    return True

def run_simple_tests():
    """Run all simple tests"""
    print("🚀 Starting Simple 27-Agent System Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("YAML Parsing", test_yaml_parsing),
        ("Engine Syntax", test_engine_syntax),
        ("Agent Count", test_agent_count)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Unexpected error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<10} {test_name}")
    
    print("-" * 50)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED! File structure is correct!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)