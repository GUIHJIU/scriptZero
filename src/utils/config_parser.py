"""
配置解析器
解析YAML/JSON格式的配置文件
"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union


class ConfigParser:
    """配置解析器"""
    
    @staticmethod
    def parse_yaml(file_path: str) -> Dict[str, Any]:
        """解析YAML配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def parse_json(file_path: str) -> Dict[str, Any]:
        """解析JSON配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def parse_config(file_path: str) -> Dict[str, Any]:
        """根据文件扩展名自动解析配置文件"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.yaml' or ext == '.yml':
            return ConfigParser.parse_yaml(file_path)
        elif ext == '.json':
            return ConfigParser.parse_json(file_path)
        else:
            raise ValueError(f"Unsupported config file format: {ext}")
    
    @staticmethod
    def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
        """验证配置是否包含必需的键"""
        for key in required_keys:
            if key not in config:
                return False
        return True
    
    @staticmethod
    def expand_variables(config: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
        """展开配置中的变量引用（如 ${variables.game_path}）"""
        import re
        
        def replace_vars(obj):
            if isinstance(obj, str):
                # 查找并替换 ${...} 格式的变量引用
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, obj)
                
                for match in matches:
                    # 解析变量路径，例如 "variables.game_path"
                    parts = match.split('.')
                    if len(parts) >= 2 and parts[0] in variables:
                        var_dict = variables
                        for part in parts[1:]:
                            var_dict = var_dict.get(part, '')
                        
                        obj = obj.replace(f"${{{match}}}", str(var_dict))
                
                return obj
            elif isinstance(obj, dict):
                return {k: replace_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            else:
                return obj
        
        return replace_vars(config)


# 示例配置文件内容
EXAMPLE_CONFIG_YAML = """
version: 1.0
name: "MMORPG日常任务自动化"

# 全局变量
variables:
  game_path: "C:/Games/MMORPG/game.exe"
  account: "player123"
  character: "warrior"

# 游戏配置
games:
  mmorpg:
    executable: "${variables.game_path}"
    arguments: ["-windowed", "-dx11"]
    working_dir: "C:/Games/MMORPG/"
    window_title: "MMORPG*"  # 支持通配符
    detection:
      type: "image"
      templates:
        - "templates/main_menu.png"
        - "templates/character_select.png"

# 脚本链
workflow:
  - name: "启动游戏并登录"
    type: "game"
    game: "mmorpg"
    actions:
      - type: "launch"
      - type: "wait_for"
        condition: "window_active"
        timeout: 30
      - type: "input"
        sequence: [
          {"key": "ENTER", "delay": 1},
          {"text": "${variables.account}", "delay": 0.5},
          {"key": "TAB", "delay": 0.5},
          {"text": "password123", "delay": 0.5},
          {"key": "ENTER", "delay": 2}
        ]

  - name: "日常任务循环"
    type: "script_chain"
    repeat: "daily"  # 支持 daily/hourly/cron表达式
    scripts:
      - path: "scripts/daily_quests.py"
        arguments: ["--character", "${variables.character}"]
        completion:  # 完成条件
          any_of:  # 任一条件满足即完成
            - type: "process_exit"
              code: 0
            - type: "timeout"
              seconds: 3600
            - type: "image_detected"
              template: "templates/quest_complete.png"
        
      - path: "scripts/auto_farming.exe"
        depends_on: "daily_quests.py"
        conditions:  # 执行条件
          all_of:  # 所有条件满足才执行
            - type: "resource_check"
              cpu_max: 70
            - type: "time_window"
              start: "02:00"
              end: "06:00"
"""

if __name__ == "__main__":
    # 创建示例配置文件用于测试
    with open("example_config.yaml", "w", encoding="utf-8") as f:
        f.write(EXAMPLE_CONFIG_YAML)
    
    # 测试配置解析
    parser = ConfigParser()
    config = parser.parse_config("example_config.yaml")
    print("配置解析成功!")
    
    # 测试变量展开
    expanded_config = parser.expand_variables(config, {
        'variables': {
            'game_path': 'C:/Games/MMORPG/game.exe',
            'account': 'player123',
            'character': 'warrior'
        }
    })
    print("变量展开完成!")