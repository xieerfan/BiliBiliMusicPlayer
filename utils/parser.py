import re

def extract_bvid(text):
    """从 URL 或文本中提取 BV 号"""
    match = re.search(r"(BV[a-zA-Z0-9]{10})", text)
    return match.group(1) if match else None

def parse_range(input_str, max_val):
    """解析 1-5, 8 或 all 这种范围输入"""
    if input_str.lower() == 'all':
        return list(range(1, max_val + 1))
    indexes = set()
    try:
        parts = input_str.replace(" ", "").split(",")
        for part in parts:
            if "-" in part:
                start, end = map(int, part.split("-"))
                indexes.update(range(start, end + 1))
            else:
                if part:
                    indexes.add(int(part))
        return sorted([i for i in indexes if 1 <= i <= max_val])
    except:
        return []