import os
from typing import List, Dict, Any

# ! Untested: Needs integration and test coverage.
from typing import List, Dict, Any, Optional
import os

def get_candid_images_metadata(
    candid_dir: Optional[str] = None,
    supported_exts: Optional[set] = None,
    images: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Returns metadata for candid images. If 'images' is provided, returns it directly (API-style usage).
    Otherwise, scans candid_dir for image files and returns their metadata.
    Args:
        candid_dir: Directory to scan for images.
        supported_exts: Set of file extensions to include (e.g., {'.jpg', '.png'}). Defaults to common image types.
        images: Optional list of image metadata dicts (API payload).
    Returns:
        List of metadata dicts for each image found or provided.
    """
    if images is not None:
        return images
    if supported_exts is None:
        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    meta_list = []
    if candid_dir is None:
        return meta_list
    for root, dirs, files in os.walk(candid_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported_exts:
                fpath = os.path.join(root, fname)
                stat = os.stat(fpath)
                meta = {
                    'filename': fname,
                    'relative_path': os.path.relpath(fpath, candid_dir),
                    'size_bytes': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                }
                meta_list.append(meta)
    return meta_list

def find_best_candid_image(query: str, candid_dir: Optional[str] = None, images: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns metadata for the image whose filename best matches the query.
    If 'images' is provided, uses it (API-style); otherwise, loads from candid_dir.
    Uses fuzzy string matching if rapidfuzz is available, else falls back to substring search.
    Returns None if no match is found.
    """
    images_list = get_candid_images_metadata(candid_dir=candid_dir, images=images)
    if not images_list:
        return None
    try:
        from rapidfuzz import process
        choices = [img['filename'] for img in images_list]
        best, score, idx = process.extractOne(query, choices)
        if score > 60:
            return images_list[idx]
    except ImportError:
        # Fallback: normalized substring match
        def normalize(s):
            s = os.path.splitext(s)[0]  # remove extension
            return s.replace('_', ' ').replace('-', ' ').lower()
        norm_query = normalize(query)
        for img in images_list:
            if norm_query in normalize(img['filename']):
                return img
    return None

def get_candid_image_by_filename(filename: str, candid_dir: Optional[str] = None, images: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns metadata for the image with the given filename in candid_dir or images list, or None if not found.
    """
    images_list = get_candid_images_metadata(candid_dir=candid_dir, images=images)
    for img in images_list:
        if img['filename'] == filename:
            return img
    return None
    return None

# todo: Add blob storage integration if needed (e.g., upload to S3/Cloudinary and return blob URLs/metadata)
