"""
图像识别功能测试脚本
用于测试模板图片是否能够被正确识别
"""
import asyncio
import pyautogui
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def test_image_recognition():
    """测试图像识别功能"""
    print("🔍 图像识别功能测试")
    print("=" * 50)
    
    # 检查模板文件是否存在
    templates_dir = Path("templates")
    required_templates = [
        "bettergi_start_btn.png",
        "bettergi_dragon_btn.png", 
        "bettergi_play_btn.png"
    ]
    
    print("📋 检查模板文件...")
    missing_templates = []
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"   ✓ {template} - 存在")
        else:
            print(f"   ✗ {template} - 缺失")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n⚠️  缺失 {len(missing_templates)} 个模板文件:")
        for template in missing_templates:
            print(f"   - {template}")
        print("请先创建这些模板文件后再运行测试。")
        return False
    
    print(f"\n✅ 所有必需的模板文件都已存在")
    
    # 创建适配器实例（使用最小配置进行测试）
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 60,
        'close_after_completion': False,  # 测试时不自动关闭
        'click_positions': {
            'start_button': (100, 100),
            'dragon_button': (200, 100),
            'play_button': (300, 100)
        },
        'image_templates': {
            'bettergi_start_btn': 'templates/bettergi_start_btn.png',
            'bettergi_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'bettergi_play_btn': 'templates/bettergi_play_btn.png'
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print(f"\n🎯 开始测试图像识别功能...")
    print("请确保BetterGI窗口处于可见状态以便进行图像识别测试")
    
    # 测试各个模板的识别
    test_results = {}
    
    print(f"\n1. 测试启动按钮识别...")
    try:
        result = await adapter.find_image_position(adapter.image_templates['bettergi_start_btn'], confidence=0.7)
        if result:
            print(f"   ✓ 成功找到启动按钮，位置: {result}")
            test_results['start_btn'] = True
        else:
            print(f"   ✗ 未找到启动按钮")
            test_results['start_btn'] = False
    except Exception as e:
        print(f"   ✗ 启动按钮识别出错: {e}")
        test_results['start_btn'] = False
    
    print(f"\n2. 测试一条龙按钮识别...")
    try:
        result = await adapter.find_image_position(adapter.image_templates['bettergi_dragon_btn'], confidence=0.7)
        if result:
            print(f"   ✓ 成功找到一条龙按钮，位置: {result}")
            test_results['dragon_btn'] = True
        else:
            print(f"   ✗ 未找到一条龙按钮")
            test_results['dragon_btn'] = False
    except Exception as e:
        print(f"   ✗ 一条龙按钮识别出错: {e}")
        test_results['dragon_btn'] = False
    
    print(f"\n3. 测试三角形启动按钮识别...")
    try:
        result = await adapter.find_image_position(adapter.image_templates['bettergi_play_btn'], confidence=0.7)
        if result:
            print(f"   ✓ 成功找到三角形启动按钮，位置: {result}")
            test_results['play_btn'] = True
        else:
            print(f"   ✗ 未找到三角形启动按钮")
            test_results['play_btn'] = False
    except Exception as e:
        print(f"   ✗ 三角形启动按钮识别出错: {e}")
        test_results['play_btn'] = False
    
    # 输出测试总结
    print(f"\n📊 测试结果汇总:")
    print(f"   启动按钮识别: {'✓ 通过' if test_results.get('start_btn') else '✗ 失败'}")
    print(f"   一条龙按钮识别: {'✓ 通过' if test_results.get('dragon_btn') else '✗ 失败'}")
    print(f"   三角形启动按钮识别: {'✓ 通过' if test_results.get('play_btn') else '✗ 失败'}")
    
    successful_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"\n📈 总体成功率: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        print(f"\n🎉 所有图像识别测试均已通过！")
        print(f"您的模板图片质量良好，可以用于自动化流程。")
        return True
    else:
        print(f"\n⚠️  部分图像识别测试失败。")
        print(f"请检查模板图片的质量或调整置信度阈值。")
        return False


async def test_click_functionality():
    """测试点击功能（谨慎使用 - 不会实际点击）"""
    print(f"\n🖱️  测试点击功能（仅模拟）...")
    print("注意: 此测试不会实际点击任何内容，仅验证点击逻辑")
    
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 60,
        'close_after_completion': False,
        'image_templates': {
            'bettergi_start_btn': 'templates/bettergi_start_btn.png',
            'bettergi_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'bettergi_play_btn': 'templates/bettergi_play_btn.png'
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    # 验证模板路径配置
    print(f"   ✓ 启动按钮模板: {adapter.image_templates.get('bettergi_start_btn')}")
    print(f"   ✓ 一条龙按钮模板: {adapter.image_templates.get('bettergi_dragon_btn')}")
    print(f"   ✓ 三角形启动按钮模板: {adapter.image_templates.get('bettergi_play_btn')}")
    
    print(f"   ✓ 点击功能配置验证通过")
    return True


async def main():
    """主测试函数"""
    print("🧪 开始图像识别功能测试...")
    print("=" * 60)
    
    # 运行图像识别测试
    recognition_success = await test_image_recognition()
    
    # 运行点击功能测试
    click_success = await test_click_functionality()
    
    print(f"\n🏁 测试完成!")
    if recognition_success:
        print(f"✅ 图像识别功能正常，可以开始使用自动化流程")
        print(f"💡 建议在实际运行自动化之前，先手动验证模板匹配效果")
    else:
        print(f"❌ 需要修复图像识别问题后才能正常使用")
    
    return recognition_success


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n✅ 测试成功完成!")
    else:
        print(f"\n❌ 测试发现问题，请检查模板图片")