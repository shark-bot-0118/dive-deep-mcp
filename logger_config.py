import os
import sys
from datetime import datetime
from loguru import logger
from typing import Any

class LoggerConfig:
    def __init__(self, app_name: str = "dive_deep"):
        self.app_name = app_name
        # プロジェクトのルートディレクトリを取得
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        # logsディレクトリのパスを設定
        self.log_dir = os.path.join(self.root_dir, "logs")
        # logsディレクトリが存在しない場合は作成
        os.makedirs(self.log_dir, exist_ok=True)
        
    def setup_logger(self):
        """ロガーの設定を行います"""
        # すべての既存のハンドラを削除
        logger.remove()
        
        # 日付ごとのログファイル名を生成
        log_file = os.path.join(
            self.log_dir,
            f"{self.app_name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # コンソール出力の設定
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # ファイル出力の設定
        logger.add(
            log_file,
            rotation="00:00",  # 毎日0時にローテーション
            retention="30 days",  # 30日分保持
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            encoding="utf-8"
        )
        
        return logger

def get_logger(app_name: str = "dive_deep") -> Any:
    """ロガーのインスタンスを取得します"""
    logger_config = LoggerConfig(app_name)
    return logger_config.setup_logger() 