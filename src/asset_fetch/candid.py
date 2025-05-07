import os
from typing import List, Dict, Any

# ! Untested: Needs integration and test coverage.
def get_candid_images_metadata(
    candid_dir: str,
    supported_exts: 'set[str]' = None
) -> List[Dict[str, Any]]:
    """
    Scans the given candid_dir for images and returns project-structured metadata for each image file.
    Args:
        candid_dir: Directory to scan for images.
        supported_exts: Set of file extensions to include (e.g., {'.jpg', '.png'}). Defaults to common image types.
    Returns:
        List of metadata dicts for each image found.
    """
    
    if supported_exts is None:
        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    meta_list = []
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

def find_best_candid_image(query: str, candid_dir: str) -> Dict[str, Any]:
    """
    Returns metadata for the image in candid_dir whose filename best matches the query.
    Uses fuzzy string matching if rapidfuzz is available, else falls back to substring search.
    Returns None if no match is found.
    """
    images = get_candid_images_metadata(candid_dir)
    if not images:
        return None
    try:
        from rapidfuzz import process
        choices = [img['filename'] for img in images]
        best, score, idx = process.extractOne(query, choices)
        if score > 60:
            return images[idx]
    except ImportError:
        # Fallback: normalized substring match
        def normalize(s):
            import os
            s = os.path.splitext(s)[0]  # remove extension
            return s.replace('_', ' ').replace('-', ' ').lower()
        norm_query = normalize(query)
        for img in images:
            if norm_query in normalize(img['filename']):
                return img
    return None

def get_candid_image_by_filename(filename: str, candid_dir: str) -> Dict[str, Any]:
    """
    Returns metadata for the image with the given filename in candid_dir, or None if not found.
    """
    images = get_candid_images_metadata(candid_dir)
    for img in images:
        if img['filename'] == filename:
            return img
    return None

# todo: Add blob storage integration if needed (e.g., upload to S3/Cloudinary and return blob URLs/metadata)
