import os
import sys
import subprocess

# 支持的文件扩展名
EXTS = ['.cpp', '.cc', '.c', '.h', '.hpp', '.hh']
CLANG_FORMAT = 'clang-format'

def format_file(file_path):
    try:
        subprocess.run([CLANG_FORMAT, '-i', file_path], check=True)
        print(f"Formatted: {file_path}")
    except Exception as e:
        print(f"Failed: {file_path} ({e})")

def main():
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    else:
        src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    print(f"Formatting directory: {src_dir}")
    for root, _, files in os.walk(src_dir):
        for f in files:
            if any(f.endswith(ext) for ext in EXTS):
                format_file(os.path.join(root, f))

if __name__ == '__main__':
    main()
