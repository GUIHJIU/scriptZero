"""
BetterGI界面状态测试脚本
用于测试不同界面状态下各按钮的识别情况
"""
import asyncio
import pyautogui
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def test_bettergi_states():
    """测试BetterGI的不同界面状态"""
    print("🔍 BetterGI界面状态测试")
    print("=" * 60)
    
    # 检查所有相关模板文件
    templates_dir = Path("templates")
    state_templates = {
        "初始启动按钮": ["bettergi_initial_start_btn.png", "bettergi_start_btn.png"],
        "一条龙按钮（前）": ["bettergi_dragon_btn_before.png", "bettergi_dragon_btn.png"],
        "蓝色启动按钮": ["bettergi_blue_play_btn.png", "bettergi_play_btn.png"]
    }
    
    print("📋 检查模板文件...")
    available_templates = {}
    
    for state_name, template_list in state_templates.items():
        print(f"\n{state_name}:")
        available_for_state = []
        for template in template_list:
            template_path = templates_dir / template
            if template_path.exists():
                print(f"   ✓ {template}")
                available_for_state.append(str(template_path))
            else:
                print(f"   ✗ {template} (缺失)")
        available_templates[state_name] = available_for_state
    
    print(f"\n🎯 开始测试界面状态识别...")
    print("请确保BetterGI窗口处于期望的界面状态")
    
    # 创建适配器实例
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 60,
        'close_after_completion': False,
        'image_templates': {
            'bettergi_initial_start_btn': 'templates/bettergi_initial_start_btn.png',
            'bettergi_dragon_btn_before': 'templates/bettergi_dragon_btn_before.png',
            'bettergi_blue_play_btn': 'templates/bettergi_blue_play_btn.png',
            'bettergi_start_btn': 'templates/bettergi_start_btn.png',
            'bettergi_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'bettergi_play_btn': 'templates/bettergi_play_btn.png'
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    # 测试各状态模板
    results = {}
    
    print(f"\n1. 测试初始启动按钮识别...")
    initial_templates = [
        t for t in available_templates["初始启动按钮"] if Path(t).exists()
    ]
    if initial_templates:
        result = await adapter.find_multiple_templates(initial_templates, confidence=0.7)
        results['initial_start'] = result is not None
        print(f"   结果: {'✓ 成功' if result else '✗ 失败'}")
        if result:
            print(f"   位置: {result}")
    else:
        print("   跳过 - 无可用模板")
        results['initial_start'] = False
    
    print(f"\n2. 测试一条龙按钮识别...")
    dragon_templates = [
        t for t in available_templates["一条龙按钮（前）"] if Path(t).exists()
    ]
    if dragon_templates:
        result = await adapter.find_multiple_templates(dragon_templates, confidence=0.7)
        results['dragon_btn'] = result is not None
        print(f"   结果: {'✓ 成功' if result else '✗ 失败'}")
        if result:
            print(f"   位置: {result}")
    else:
        print("   跳过 - 无可用模板")
        results['dragon_btn'] = False
    
    print(f"\n3. 测试蓝色启动按钮识别...")
    blue_templates = [
        t for t in available_templates["蓝色启动按钮"] if Path(t).exists()
    ]
    if blue_templates:
        result = await adapter.find_multiple_templates(blue_templates, confidence=0.7)
        results['blue_play'] = result is not None
        print(f"   结果: {'✓ 成功' if result else '✗ 失败'}")
        if result:
            print(f"   位置: {result}")
    else:
        print("   跳过 - 无可用模板")
        results['blue_play'] = False
    
    # 输出测试总结
    print(f"\n📊 状态测试结果:")
    for state, success in results.items():
        state_names = {
            'initial_start': '初始启动按钮',
            'dragon_btn': '一条龙按钮', 
            'blue_play': '蓝色启动按钮'
        }
        print(f"   {state_names.get(state, state)}: {'✓ 通过' if success else '✗ 失败'}")
    
    successful_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    print(f"\n📈 总体成功率: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    # 提供建议
    print(f"\n💡 建议:")
    if not results.get('initial_start'):
        print(f"   - 如果当前处于初始状态，需要制作初始启动按钮模板")
    if not results.get('dragon_btn'):
        print(f"   - 如果需要识别一条龙按钮，需要制作相应模板")
    if not results.get('blue_play'):
        print(f"   - 如果需要识别蓝色启动按钮，需要制作相应模板")
    
    print(f"\n🔧 操作提示:")
    print(f"   - 运行 python image_template_generator.py 可以帮助制作模板")
    print(f"   - 根据BetterGI的实际界面状态制作对应的图像模板")
    
    return successful_tests > 0  # 只要有任何一个成功就算测试部分通过


async def main():
    """主测试函数"""
    print("🧪 开始BetterGI界面状态测试...")
    print("=" * 70)
    
    success = await test_bettergi_states()
    
    print(f"\n🏁 测试完成!")
    if success:
        print(f"✅ 部分或全部状态测试通过，可以进行自动化流程")
    else:
        print(f"❌ 没有任何状态被成功识别，请检查模板文件")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n✅ 状态测试部分成功!")
    else:
        print(f"\n❌ 状态测试未通过，请制作更多模板")