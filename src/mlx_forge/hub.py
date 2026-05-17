from __future__ import annotations

from pathlib import Path
from typing import Iterable


def pull_model(model_id: str, *, cache_dir: str | Path | None = None) -> Path:
    from huggingface_hub import snapshot_download

    return Path(snapshot_download(repo_id=model_id, cache_dir=str(cache_dir) if cache_dir else None))


def list_models(*, cache_dir: str | Path | None = None) -> list[str]:
    from huggingface_hub import scan_cache_dir

    cache = scan_cache_dir(cache_dir=str(cache_dir) if cache_dir else None)
    return sorted(repo.repo_id for repo in cache.repos)


def remove_models(model_ids: Iterable[str], *, cache_dir: str | Path | None = None) -> None:
    from huggingface_hub import scan_cache_dir

    wanted = set(model_ids)
    cache = scan_cache_dir(cache_dir=str(cache_dir) if cache_dir else None)
    revisions = [
        revision.commit_hash
        for repo in cache.repos
        if repo.repo_id in wanted
        for revision in repo.revisions
    ]
    if revisions:
        cache.delete_revisions(*revisions).execute()
