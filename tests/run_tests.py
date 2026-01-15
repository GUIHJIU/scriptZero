"""
测试运行脚本
用于运行不同级别的测试并生成覆盖率报告
"""
import subprocess
import sys
import os
from pathlib import Path


def run_unit_tests():
    """运行单元测试"""
    print("运行单元测试...")
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/unit", 
        "-v", 
        "--cov=src", 
        "--cov-report=html:coverage/unit", 
        "--cov-report=term-missing"
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_integration_tests():
    """运行集成测试"""
    print("运行集成测试...")
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/integration", 
        "-v", 
        "--cov=src", 
        "--cov-report=html:coverage/integration", 
        "--cov-report=term-missing"
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_all_tests():
    """运行所有测试"""
    print("运行所有测试...")
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests", 
        "-v", 
        "--cov=src", 
        "--cov-report=html:coverage/all", 
        "--cov-report=term-missing"
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_specific_test_suite(suite_name):
    """运行特定测试套件"""
    suite_paths = {
        "adapters": "tests/unit/adapters",
        "config": "tests/unit/config",
        "utils": "tests/unit/utils",
        "genshin_bettergi": "tests/integration/genshin_bettergi",
        "workflow": "tests/integration/workflow"
    }
    
    if suite_name not in suite_paths:
        print(f"未知的测试套件: {suite_name}")
        print(f"可用的测试套件: {list(suite_paths.keys())}")
        return False
    
    print(f"运行 {suite_name} 测试套件...")
    cmd = [
        sys.executable, "-m", "pytest", 
        suite_paths[suite_name], 
        "-v", 
        "--cov=src", 
        f"--cov-report=html:coverage/{suite_name}", 
        "--cov-report=term-missing"
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def generate_coverage_report():
    """生成总体覆盖率报告"""
    print("生成总体覆盖率报告...")
    cmd = [
        sys.executable, "-m", "coverage", "combine",
        "&&",
        sys.executable, "-m", "coverage", "report",
        "&&",
        sys.executable, "-m", "coverage", "html", "-d", "coverage/overall"
    ]
    
    # 在Windows上需要特殊处理
    import platform
    if platform.system() == "Windows":
        # Windows上使用powershell命令
        cmd = f"coverage combine; coverage report; coverage html -d coverage/overall"
        result = subprocess.run(["powershell", "-Command", cmd], shell=True)
    else:
        result = subprocess.run(" ".join(cmd), shell=True)
    
    return result.returncode == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python run_tests.py unit          # 运行单元测试")
        print("  python run_tests.py integration  # 运行集成测试") 
        print("  python run_tests.py all          # 运行所有测试")
        print("  python run_tests.py <suite>      # 运行特定测试套件")
        print("  python run_tests.py coverage     # 生成覆盖率报告")
        print("")
        print("可用的测试套件:")
        print("  adapters, config, utils, genshin_bettergi, workflow")
        return
    
    command = sys.argv[1].lower()
    
    # 确保在项目根目录运行
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "all":
        success = run_all_tests()
    elif command == "coverage":
        success = generate_coverage_report()
    else:
        # 尝试运行特定测试套件
        success = run_specific_test_suite(command)
    
    if not success:
        print(f"测试执行失败: {command}")
        sys.exit(1)
    else:
        print(f"测试执行成功: {command}")


if __name__ == "__main__":
    main()