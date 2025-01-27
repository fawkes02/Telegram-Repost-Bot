import logging
from typing import List

import yaml

from strategies import STRATEGIES, DEFAULT_STRATEGY

logger = logging.getLogger(__name__)


class MissingConfigParameterException(Exception):
    pass


class NoConfigFileAvailableException(Exception):
    pass


def ensure_proper_config_structure(data: dict):
    top_level = ["repost_data_path", "bot_admin_id", "bot_token", "hash_size",
                 "repost_callout_timeout", "auto_call_out", "default_callouts", "strings"]
    defaults = ["url", "picture"]
    strings = ["private_chat", "private_chat_toggle", "help_command", "invalid_whitelist_reply",
               "removed_from_whitelist", "successful_whitelist_reply", "group_repost_reset_initial_prompt",
               "group_repost_reset_admin_only", "group_repost_reset_cancel", "group_repost_data_reset",
               "stats_command_reply"]
    for repost_strategy in STRATEGIES.values():
        strings.extend(repost_strategy.get_required_strings())

    logger.info("TESTING TOP-LEVEL FIELDS")
    test_strings(data, top_level)

    logger.info("TESTING DEFAULT CALLOUT SETTINGS")
    test_strings(data.get("default_callouts"), defaults)

    logger.info("TESTING BOT STRINGS")
    test_strings(data.get("strings"), strings)


def test_strings(data: dict, strings: List[str]):
    for field in strings:
        value_exists = data.get(field) is not None
        logger_fn = logger.info if value_exists else logger.warning
        logger_fn(f"TESTING \"{field}\"...{'FOUND' if value_exists else 'UNDEFINED'}")


def get_config_variables(config_path: str) -> tuple:
    config_data, default_config_data = None, None

    if config_path is not None:
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        except (FileNotFoundError, TypeError) as e:
            logger.warning(f"{e.strerror} -- could not find '{config_path}'")
    else:
        logger.warning("User-created config not specified. Proceeding with defaultconfig.yaml")
    try:
        with open('defaultconfig.yaml', 'r') as f:
            default_config_data = yaml.safe_load(f)
    except (FileNotFoundError, TypeError) as e:
        if config_path is None:
            raise NoConfigFileAvailableException("Default config not found and no user-created config specified. Guess I'll die.")
        else:
            logger.warning("Could not find defaultconfig.yaml. If your config.yaml is missing anything, this could be an issue.")

    default_repost_data_path, default_bot_admin_id, default_telegram_token, default_default_callouts,\
        default_bot_strings, default_hash_size, default_repost_callout_timeout, default_auto_call_out, default_strategy\
        = None, None, None, None, None, None, None, None, None

    if default_config_data is not None:
        logger.info("testing default config file for all required fields")
        ensure_proper_config_structure(default_config_data)
        default_repost_data_path = default_config_data.get("repost_data_path", None)
        default_bot_admin_id = default_config_data.get("bot_admin_id", None)
        default_telegram_token = default_config_data.get("bot_token", None)
        default_default_callouts = default_config_data.get("default_callouts", None)
        default_bot_strings = default_config_data.get("strings", None)
        default_hash_size = default_config_data.get("hash_size", None)
        default_repost_callout_timeout = default_config_data.get("repost_callout_timeout", None)
        default_auto_call_out = default_config_data.get("auto_call_out", None)
        default_strategy = default_config_data.get("callout_style", DEFAULT_STRATEGY)

    repost_data_path = default_repost_data_path
    bot_admin_id = default_bot_admin_id
    telegram_token = default_telegram_token
    default_callouts = default_default_callouts
    bot_strings = default_bot_strings
    hash_size = default_hash_size
    repost_callout_timeout = default_repost_callout_timeout
    auto_call_out = default_auto_call_out
    strategy = default_strategy

    if config_path is not None and config_data is not None:
        logger.info("testing user config file for all required fields")
        ensure_proper_config_structure(config_data)
        repost_data_path = config_data.get("repost_data_path", default_repost_data_path)
        bot_admin_id = config_data.get("bot_admin_id", default_bot_admin_id)
        telegram_token = config_data.get("bot_token", default_telegram_token)
        default_callouts = config_data.get("default_callouts", default_default_callouts)
        bot_strings = {**default_bot_strings, **config_data.get("strings", {})}
        hash_size = config_data.get("hash_size", default_hash_size)
        repost_callout_timeout = config_data.get("repost_callout_timeout", default_repost_callout_timeout)
        auto_call_out = config_data.get("auto_call_out", default_auto_call_out)
        strategy = config_data.get("callout_style", default_strategy)

    bot_variables = (repost_data_path, bot_admin_id, telegram_token, default_callouts, bot_strings, hash_size,
                     repost_callout_timeout, auto_call_out, strategy, auto_call_out)
    if any(var is None for var in bot_variables):
        print(bot_variables)
        raise MissingConfigParameterException("Missing required config parameters between default and user config files. Cannot proceed")

    return repost_data_path, bot_admin_id, telegram_token, default_callouts, bot_strings, hash_size, \
           repost_callout_timeout, auto_call_out, strategy
