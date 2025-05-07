import os
import shutil
import tempfile
import time
from asset_fetch.candid import get_candid_images_metadata, get_candid_image_by_filename, find_best_candid_image
import logging
from datetime import datetime

def create_test_images(test_dir, files):
    os.makedirs(test_dir, exist_ok=True)
    for fname in files:
        fpath = os.path.join(test_dir, fname)
        with open(fpath, 'wb') as f:
            f.write(os.urandom(1024))  # 1KB random content
        # Touch times for deterministic testing
        os.utime(fpath, (time.time() - 100, time.time() - 50))

def test_get_candid_images_metadata():
    """
    Test using a temporary directory.
    """
    test_dir = tempfile.mkdtemp()
    files = ['cat.jpg', 'dog.png', 'README.txt', 'sunset_beach.jpeg']
    create_test_images(test_dir, files)
    meta = get_candid_images_metadata(test_dir)
    names = {m['filename'] for m in meta}
    assert 'cat.jpg' in names
    assert 'dog.png' in names
    assert 'sunset_beach.jpeg' in names
    assert 'README.txt' not in names
    shutil.rmtree(test_dir)

def test_get_candid_image_by_filename():
    """
    Test using a temporary directory.
    """
    test_dir = tempfile.mkdtemp()
    files = ['cat.jpg', 'dog.png']
    create_test_images(test_dir, files)
    meta = get_candid_image_by_filename('cat.jpg', test_dir)
    assert meta is not None
    assert meta['filename'] == 'cat.jpg'
    meta_none = get_candid_image_by_filename('not_exist.jpg', test_dir)
    assert meta_none is None


# * Configure logging for test metadata
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_find_best_candid_image():
    test_name = "test_find_best_candid_image"
    params = {}
    start_time = datetime.utcnow()
    start_ts = time.time()
    logging.info(f"[META] Test: {test_name} | Start: {start_time.isoformat()} | Params: {params}")
    result = "passed"
    try:
        test_dir = tempfile.mkdtemp()
        files = ['ai_robot.jpg', 'beach_sunset.png', 'mountain_view.jpeg']
        create_test_images(test_dir, files)
        # Should match exactly
        meta = find_best_candid_image('beach sunset', test_dir)
        print("Meta for 'beach sunset':", meta)
        assert meta is not None
        assert meta['filename'] == 'beach_sunset.png'
    except Exception as e:
        result = f"failed: {e}"
        logging.error(f"[META] Test: {test_name} | Exception: {e}")
        raise
    finally:
        end_time = datetime.utcnow()
        duration = time.time() - start_ts
        logging.info(f"[META] Test: {test_name} | End: {end_time.isoformat()} | Duration: {duration:.3f}s | Result: {result} | Params: {params}")
    assert meta is not None
    assert 'beach' in meta['filename']
    # Should fallback to substring if rapidfuzz not installed
    meta2 = find_best_candid_image('robot', test_dir)
    print("Meta for 'robot':", meta2)
    assert meta2 is not None
    assert 'robot' in meta2['filename']
    # Should return None if no match
    meta_none = find_best_candid_image('notfound', test_dir)
    print("Meta for 'notfound':", meta_none)
    assert meta_none is None
    shutil.rmtree(test_dir)

def test_get_candid_images_metadata_real_dir():
    """
    Test using the real src/data/candids directory if it exists and is non-empty.
    """
    real_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/candids'))
    if not os.path.isdir(real_dir):
        return  # skip if not present
    meta = get_candid_images_metadata(real_dir)
    if not meta:
        return  # skip if empty
    for m in meta:
        assert m['filename'].lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"))

def test_find_best_candid_image_real_dir():
    """
    Test fuzzy search on the real src/data/candids directory if it exists and is non-empty.
    """
    real_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/candids'))
    if not os.path.isdir(real_dir):
        return  # skip if not present
    meta = get_candid_images_metadata(real_dir)
    if not meta:
        return  # skip if empty
    first_img = meta[0]['filename']
    best = find_best_candid_image(first_img, real_dir)
    assert best is not None
    assert best['filename'] == first_img
