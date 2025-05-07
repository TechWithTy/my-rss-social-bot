"""
main.py
Entrypoint for the RSS-to-social bot. Selects the enabled blog source and runs the workflow.
"""
from src.utils.config.config_provider import load_modular_config
from src.utils.workflow import run_rss_to_social_workflow
from src.utils.index import get_env_variable

# ! TEST_MODE disables main workflow execution for test environments
test_mode = get_env_variable("TEST_MODE").lower() == "true"

def main() -> None:
    """
    CLI Entrypoint for the bot. Selects the single enabled blog source and runs the workflow.
    """
    config = load_modular_config()  # * Load merged config from all YAML files
    if test_mode:
        raise RuntimeError(
            "! main() should not run when TEST_MODE is enabled. Turn off TEST_MODE or run tests directly."
        )
    # * Gather possible blog sources from config
    medium_username = config["user_profile"].get("medium_username")
    wix_url = config["user_profile"].get("wix_url")
    wordpress_url = config["user_profile"].get("wordpress_url")

    enabled_sources = [s for s in [medium_username, wix_url, wordpress_url] if s]

    # ! Only one source should be enabled at a time
    if len(enabled_sources) > 1:
        print("! Only one RSS source can be enabled at a time. Please check your config!")
        return
    elif not enabled_sources:
        print("! RSS Feed URL or Username Not Given In Config!")
        return

    rss_source = enabled_sources[0]
    print(f"* Running workflow for source: {rss_source}")
    import asyncio
    asyncio.run(run_rss_to_social_workflow(rss_source))


if __name__ == "__main__":
    main()
