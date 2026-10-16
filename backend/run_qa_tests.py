"""
QA Automated Test Suite Runner
Chạy toàn bộ các bộ test QA cho Phase 1, Phase 2, Phase 3 và tổng hợp kết quả.
"""
import sys
import subprocess
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("=" * 70)
    print("🔍 BẮT ĐẦU CHẠY TOÀN BỘ TEST SUITE KIỂM THỬ TÌM LỖI (QA AGENT)")
    print("=" * 70)

    test_files = [
        "tests/test_qa_phase1_auth.py",
        "tests/test_qa_phase2_rooms.py",
        "tests/test_qa_phase3_meetings.py"
    ]

    python_exe = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    overall_results = {}

    for tf in test_files:
        print(f"\n--- Đang chạy {tf} ---")
        cmd = [python_exe, "-m", "pytest", tf, "-s", "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        overall_results[tf] = result.returncode

    print("\n" + "=" * 70)
    print("📊 TỔNG HỢP KẾT QUẢ KIỂM THỬ QA:")
    print("=" * 70)
    for tf, code in overall_results.items():
        status = "⚠️ PHÁT HIỆN LỖI (FAILED TEST / BUG REPRODUCED)" if code != 0 else "✅ PASS HẾT"
        print(f"{tf:<40} : {status}")

if __name__ == "__main__":
    main()
