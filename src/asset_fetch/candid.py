import os
from typing import List, Dict, Any, Optional

# ! Untested: Needs integration and test coverage.
from typing import List, Dict, Any, Optional
import os

def get_candid_media_metadata(
    candid_dir: Optional[str] = None,
    supported_exts: Optional[set] = None,
    media: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Returns metadata for candid media assets (images, videos, audio). If 'media' is provided, returns it directly (API-style usage).
    Otherwise, scans candid_dir for media files and returns their metadata.
    Args:
        candid_dir: Directory to scan for media files.
        supported_exts: Set of file extensions to include. Defaults to common image, video, and audio types.
        media: Optional list of media metadata dicts (API payload).
    Returns:
        List of metadata dicts for each media file found or provided, with media_type.
    """
    if media is not None:
        return media
    if supported_exts is None:
        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
                          '.mp4', '.mov', '.avi', '.webm', '.mkv', '.mp3', '.wav', '.m4a'}
    meta_list = []
    if candid_dir is None:
        return meta_list
    for root, dirs, files in os.walk(candid_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported_exts:
                fpath = os.path.join(root, fname)
                stat = os.stat(fpath)
                media_type = (
                    'image' if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'} else
                    'video' if ext in {'.mp4', '.mov', '.avi', '.webm', '.mkv'} else
                    'audio' if ext in {'.mp3', '.wav', '.m4a'} else
                    'other'
                )
                meta = {
                    'filename': fname,
                    'relative_path': os.path.relpath(fpath, candid_dir),
                    'size_bytes': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'media_type': media_type
                }
                meta_list.append(meta)
    return meta_list

def find_best_candid_media(query: str, candid_dir: Optional[str] = None, media: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns metadata for the media file whose filename best matches the query.
    If 'media' is provided, uses it (API-style); otherwise, loads from candid_dir.
    Uses fuzzy string matching if rapidfuzz is available, else falls back to substring search.
    Returns None if no match is found.
    """
    media_list = get_candid_media_metadata(candid_dir=candid_dir, media=media)
    if not media_list:
        return None
    try:
        from rapidfuzz import process
        choices = [m['filename'] for m in media_list]
        best, score, idx = process.extractOne(query, choices)
        if score > 60:
            return media_list[idx]
    except ImportError:
        # Fallback: normalized substring match
        def normalize(s):
            s = os.path.splitext(s)[0]  # remove extension
            return s.replace('_', ' ').replace('-', ' ').lower()
        norm_query = normalize(query)
        for m in media_list:
            if norm_query in normalize(m['filename']):
                return m
    return None

def get_candid_media_by_filename(filename: str, candid_dir: Optional[str] = None, media: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns metadata for the media file with the given filename in candid_dir or media list, or None if not found.
    """
    media_list = get_candid_media_metadata(candid_dir=candid_dir, media=media)
    for m in media_list:
        if m['filename'] == filename:
            return m
    return None

# todo: Add blob storage integration if needed (e.g., upload to S3/Cloudinary and return blob URLs/metadata)
