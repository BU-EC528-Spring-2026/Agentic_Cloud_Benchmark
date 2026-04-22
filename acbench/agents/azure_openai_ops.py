"""Azure OpenAI-backed ops agent integration for ACBench."""

from __future__ import annotations

from acbench.agents.openai_ops import OpenAIOpsAgent


def _contains_placeholder(value: str) -> bool:
    """Return whether one Azure config field still contains template markers."""

    return "<" in value or ">" in value


class AzureOpenAIOpsAgent(OpenAIOpsAgent):
    """OpenAI-compatible ops agent configured for Azure OpenAI credentials."""

    def configure(
        self,
        run_config=None,
        *,
        model: str = "",
        api_key_env: str = "AZURE_OPENAI_API_KEY",
        base_url: str = "",
        **kwargs,
    ) -> None:
        """Load runtime configuration before the problem starts."""

        if run_config is not None:
            section = dict(getattr(run_config, "ops_agent_config", {}) or {})
            model = str(
                section.get(
                    "model",
                    getattr(run_config, "openai_model", model),
                )
            ).strip()

            api_key_env = str(
                section.get(
                    "api_key_env", 
                    getattr(run_config, "openai_api_key_env", api_key_env),
                )
            ).strip()
            base_url = str(
                section.get(
                    "base_url", 
                    getattr(run_config, "openai_base_url", base_url),
                )
            ).strip()

        if not model:
            raise ValueError(
                "AzureOpenAIOpsAgent requires `ops.model` set to your Azure deployment name."
            )
        if _contains_placeholder(model):
            raise ValueError(
                "AzureOpenAIOpsAgent `ops.model` still contains a placeholder. "
                "Replace `<your deployment name>` with your actual Azure deployment name."
            )
        if not base_url:
            raise ValueError(
                "AzureOpenAIOpsAgent requires `ops.base_url` (for example `https://<resource>.openai.azure.com/openai/v1/`)."
            )
        if _contains_placeholder(base_url):
            raise ValueError(
                "AzureOpenAIOpsAgent `ops.base_url` still contains a placeholder. "
                "Replace `<resource>` with your actual Azure resource host."
            )

        super().configure(
            run_config=run_config,
            model=model,
            api_key_env=api_key_env,
            base_url=base_url,
            **kwargs,
        )
