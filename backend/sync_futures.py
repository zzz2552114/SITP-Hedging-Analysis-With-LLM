"""
Tushare 期货数据同步脚本
用法：
    python sync_futures.py --mode contracts           # 同步合约基本信息
    python sync_futures.py --mode kline               # 同步所有合约近N年日K
    python sync_futures.py --mode kline --code CU2501.SHF  # 同步单个合约
    python sync_futures.py --mode all                 # 先同步合约，再同步K线
"""

import sys
import os
import asyncio
import argparse
import time
from datetime import datetime, timedelta

# 加拼音库（可选，没有时退回首字母提取）
try:
    from pypinyin import lazy_pinyin
    HAS_PINYIN = True
except ImportError:
    HAS_PINYIN = False

import tushare as ts
from tortoise import Tortoise

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import TORTOISE_ORM
from app.models import FuturesContract, FuturesDailyKline

TOKEN = os.environ.get("TUSHARE_TOKEN", "")
if not TOKEN:
    raise RuntimeError("请设置环境变量 TUSHARE_TOKEN，例如: export TUSHARE_TOKEN=your_token")
pro = ts.pro_api(TOKEN)

# 全交易所
EXCHANGES = ["SHFE", "DCE", "CZCE", "CFFEX", "INE", "GFEX"]

# 品种名称 → 首字母（硬编码常用品种，减少拼音库依赖）
MANUAL_PINYIN: dict[str, str] = {
    "铜": "T", "铝": "L", "锌": "X", "铅": "Q", "镍": "N", "锡": "X",
    "黄金": "H", "白银": "B", "螺纹钢": "L", "热轧卷板": "R", "线材": "X",
    "不锈钢": "B", "铁矿石": "T", "焦炭": "J", "焦煤": "J", "动力煤": "D",
    "天然橡胶": "T", "纸浆": "Z", "燃料油": "R", "沥青": "L",
    "原油": "Y", "低硫燃料油": "D",
    "豆一": "D", "豆二": "D", "豆粕": "D", "豆油": "D",
    "棕榈油": "Z", "玉米": "Y", "玉米淀粉": "Y", "鸡蛋": "J",
    "生猪": "S", "粳米": "J", "纤维板": "X", "胶合板": "J",
    "聚乙烯": "J", "聚氯乙烯": "J", "聚丙烯": "J", "乙二醇": "Y",
    "苯乙烯": "B", "液化石油气": "Y",
    "棉花": "M", "白糖": "B", "菜籽油": "C", "菜粕": "C",
    "甲醇": "J", "PTA": "P", "对二甲苯": "D", "短纤": "D",
    "玻璃": "B", "纯碱": "C", "尿素": "N", "苹果": "P",
    "红枣": "H", "花生": "H",
    "沪深300": "H", "中证500": "Z", "中证1000": "Z",
    "上证50": "S", "10年期国债": "N", "5年期国债": "N", "2年期国债": "N",
    "30年期国债": "S",
    "工业硅": "G", "碳酸锂": "T", "多晶硅": "D", "氧化铝": "Y",
}


def fix_encoding(s: str) -> str:
    """尝试修复 Tushare 返回的 GBK 乱码字符串"""
    if not s:
        return s
    try:
        # 如果已是合法 UTF-8 中文则直接返回
        s.encode('utf-8').decode('utf-8')
        # 再检查是否含中文，若没有中文且非纯 ASCII 说明可能是乱码
        has_cjk = any('一' <= c <= '鿿' for c in s)
        if has_cjk or s.isascii():
            return s
        # 尝试 latin-1 → gbk 修复
        return s.encode('latin-1').decode('gbk', errors='replace')
    except Exception:
        try:
            return s.encode('latin-1').decode('gbk', errors='replace')
        except Exception:
            return s


def get_pinyin_initial(name: str, fut_code: str = "") -> str:
    """从品种中文名提取首字母，失败时回落到合约代码首字母"""
    for key, val in MANUAL_PINYIN.items():
        if name.startswith(key):
            return val.upper()
    if HAS_PINYIN:
        try:
            py = lazy_pinyin(name[0])
            if py and py[0][0].isalpha():
                return py[0][0].upper()
        except Exception:
            pass
    # 兜底：取 fut_code 的字母部分首字母，避免取到数字
    return get_initial_from_code(fut_code) if fut_code else "#"


def get_initial_from_code(fut_code: str) -> str:
    """从合约代码提取字母首字母"""
    alpha = ''.join(c for c in fut_code if c.isalpha())
    return alpha[0].upper() if alpha else "#"


async def sync_contracts():
    """同步所有交易所的合约基本信息到 futures_contract 表"""
    print("开始同步合约基本信息...")
    total = 0
    for exchange in EXCHANGES:
        try:
            df = pro.fut_basic(exchange=exchange, fields="ts_code,symbol,name,fut_code,list_date,delist_date")
            if df is None or df.empty:
                continue
            for _, row in df.iterrows():
                ts_code = str(row["ts_code"]).strip()
                name = fix_encoding(str(row.get("name", "") or "").strip())
                fut_code = str(row.get("fut_code", "") or "").strip()
                pinyin_initial = get_pinyin_initial(name, fut_code)

                await FuturesContract.update_or_create(
                    ts_code=ts_code,
                    defaults={
                        "symbol": str(row.get("symbol", "") or "").strip(),
                        "name": name,
                        "exchange": exchange,
                        "fut_code": fut_code,
                        "pinyin_initial": pinyin_initial,
                        "list_date": str(row.get("list_date", "") or "") or None,
                        "delist_date": str(row.get("delist_date", "") or "") or None,
                    }
                )
                total += 1
            print(f"  {exchange}: {len(df)} 条合约")
            time.sleep(0.3)  # Tushare 频率限制
        except Exception as e:
            print(f"  {exchange} 失败: {e}")
    print(f"合约同步完成，共 {total} 条")


async def sync_kline_for_code(ts_code: str, start_date: str, end_date: str):
    """同步单个合约的日K数据"""
    try:
        df = pro.fut_daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields="ts_code,trade_date,pre_close,pre_settle,open,high,low,close,settle,change1,change2,vol,amount,oi,oi_chg"
        )
        if df is None or df.empty:
            return 0

        records = []
        for _, row in df.iterrows():
            def safe_float(val):
                try:
                    v = float(val)
                    return None if (v != v) else v  # NaN check
                except Exception:
                    return None

            records.append({
                "ts_code_id": str(row["ts_code"]).strip(),
                "trade_date": str(row["trade_date"]).strip(),
                "pre_close": safe_float(row.get("pre_close")),
                "pre_settle": safe_float(row.get("pre_settle")),
                "open": safe_float(row.get("open")),
                "high": safe_float(row.get("high")),
                "low": safe_float(row.get("low")),
                "close": safe_float(row.get("close")),
                "settle": safe_float(row.get("settle")),
                "change1": safe_float(row.get("change1")),
                "change2": safe_float(row.get("change2")),
                "vol": safe_float(row.get("vol")),
                "amount": safe_float(row.get("amount")),
                "oi": safe_float(row.get("oi")),
                "oi_chg": safe_float(row.get("oi_chg")),
            })

        # 批量 upsert（Tortoise 不原生支持 bulk upsert，逐条用 update_or_create）
        for rec in records:
            await FuturesDailyKline.update_or_create(
                ts_code_id=rec["ts_code_id"],
                trade_date=rec["trade_date"],
                defaults={k: v for k, v in rec.items() if k not in ("ts_code_id", "trade_date")}
            )
        return len(records)
    except Exception as e:
        print(f"    {ts_code} K线同步失败: {e}")
        return 0


async def sync_kline_all(years_back: int = 3, single_code: str = None, only_main: bool = False):
    """同步合约日K数据。only_main=True 时只同步各品种主力合约（ts_code 字母部分无数字且不含 L 后缀）"""
    end_date = datetime.today().strftime("%Y%m%d")
    start_date = (datetime.today() - timedelta(days=365 * years_back)).strftime("%Y%m%d")
    print(f"日K同步范围: {start_date} ~ {end_date}")

    if single_code:
        codes = [single_code]
    else:
        all_codes = await FuturesContract.all().values_list("ts_code", flat=True)
        if only_main:
            # 主力合约：'.' 前的部分全是字母且不以 L 结尾（排除连续合约）
            codes = [c for c in all_codes if c.split('.')[0].isalpha() and not c.split('.')[0].endswith('L')]
        else:
            codes = list(all_codes)

    print(f"待同步合约数: {len(codes)}")
    total_bars = 0
    for i, code in enumerate(codes):
        n = await sync_kline_for_code(code, start_date, end_date)
        total_bars += n
        print(f"  [{i+1}/{len(codes)}] {code}: {n} 条")
        time.sleep(0.3)

    print(f"K线同步完成，共 {total_bars} 条")


async def main():
    parser = argparse.ArgumentParser(description="Tushare 期货数据同步")
    parser.add_argument("--mode", choices=["contracts", "kline", "all"], default="all")
    parser.add_argument("--code", type=str, default=None, help="单独同步某合约 ts_code")
    parser.add_argument("--years", type=int, default=3, help="K线回溯年数，默认3年")
    parser.add_argument("--only-main", action="store_true", help="只同步各品种主力合约")
    args = parser.parse_args()

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    try:
        if args.mode in ("contracts", "all"):
            await sync_contracts()
        if args.mode in ("kline", "all"):
            await sync_kline_all(years_back=args.years, single_code=args.code, only_main=args.only_main)
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
