"""
窗口标题调试工具
用于找出BetterGI和原神的实际窗口标题
"""
import pygetwindow as gw
import time


def debug_window_titles():
    """调试窗口标题"""
    print("🔍 窗口标题调试工具")
    print("=" * 40)
    print("请确保BetterGI和原神都已经启动")
    print("按Enter键获取当前所有窗口标题...")
    
    input()
    
    print("\n📋 当前所有窗口标题:")
    titles = gw.getAllTitles()
    
    bettergi_related = []
    genshin_related = []
    
    for i, title in enumerate(titles):
        print(f"{i+1:2d}. {title}")
        
        # 检查是否与BetterGI相关
        if any(keyword in title.lower() for keyword in ['better', 'gi', 'bg']):
            bettergi_related.append((i+1, title))
        
        # 检查是否与原神相关
        if any(keyword in title for keyword in ['原神', 'genshin', 'yuan', 'impact']):
            genshin_related.append((i+1, title))
    
    print(f"\n🔍 检测到的BetterGI相关窗口 ({len(bettergi_related)} 个):")
    for idx, title in bettergi_related:
        print(f"   {idx}. {title}")
    
    print(f"\n🔍 检测到的原神相关窗口 ({len(genshin_related)} 个):")
    for idx, title in genshin_related:
        print(f"   {idx}. {title}")
    
    if bettergi_related:
        print(f"\n💡 BetterGI窗口标题建议配置:")
        for _, title in bettergi_related:
            print(f"   window_title: \"{title}\"")
    
    if genshin_related:
        print(f"\n💡 原神窗口标题建议配置:")
        for _, title in genshin_related:
            print(f"   window_title: \"{title}\"")


if __name__ == "__main__":
    debug_window_titles()