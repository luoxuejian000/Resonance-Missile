# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
全局配置管理
基于晶脉哲学四重公理：所有参数均可追溯、可协商、可审计。
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    hub_host: str = "0.0.0.0"
    hub_port: int = 8000
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    lambda_u: float = 0.4
    lambda_d: float = 0.2
    lambda_a: float = 0.4

    a_inert_threshold: float = 0.01
    a_boundary_low: float = 0.12
    a_boundary_high: float = 0.9
    sigma_d_window: int = 5
    u_peak_lookback: int = 3
    u_delta_reversal: float = -0.05

    tuning_alpha: float = 0.1
    tuning_beta: float = 0.05
    tuning_gamma: float = 0.02
    initial_temperature: float = 1.0

    human_approval_required: bool = True
    max_auto_fix_attempts: int = 0

    audit_log_path: str = "audit.jsonl"
    thinkcheck_path: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()