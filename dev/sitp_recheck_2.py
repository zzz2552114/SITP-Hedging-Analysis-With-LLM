import os
import json
import glob
import copy
import fitz
from openai import OpenAI


API_KEY = None
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# 模型版本
MODEL_DEEPSEEK = "deepseek-v3.2"
MODEL_QWEN_TRANS = "qwen-plus-2025-09-11"
MODEL_QWEN_NORM = "qwen-plus-2025-09-11"
MODEL_QWEN_VALIDATE = "qwen3-max"
# 目录等设置 (修改为相对根目录的统一存放路径，避免找不到目录报错并在后续被参数覆盖)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT_DIR, "data", "pdfs")
OUT_DIR = os.path.join(ROOT_DIR, "data", "out_txt")
MAX_CHARS = 200_000

# 是否启用 Qwen 验证
ENABLE_VALIDATION = True
# 是否启用“验证后自动修正”
AUTO_FIX_FROM_VALIDATION = True

# pdf处理
def pdf_to_text_by_page(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for i in range(doc.page_count):
        t = doc[i].get_text("text") or ""
        parts.append(f"<<<<PAGE {i+1}>>>>\n{t.strip()}\n")
    return "\n".join(parts)[:MAX_CHARS]

# json提取
def extract_json_object(text: str) -> str:
    a = text.find("{")
    b = text.rfind("}")
    if a == -1 or b == -1 or b <= a:
        raise ValueError("模型输出找不到 JSON 对象")
    return text[a:b + 1]

def llm_json(model: str, system: str, user: str) -> dict:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.1,
    )
    content = (resp.choices[0].message.content or "").replace("```json", "").replace("```", "").strip()
    return json.loads(extract_json_object(content))

# deepseek_schema
SCHEMA = {
  "meta": {
    "company_name": {"value": None, "evidence": {"page": None, "quote": None}},
    "stock_code": {"value": None, "evidence": {"page": None, "quote": None}},
    "stock_short_name": {"value": None, "evidence": {"page": None, "quote": None}},
    "announcement_title": {"value": None, "evidence": {"page": None, "quote": None}},
    "announcement_date": {"value": None, "evidence": {"page": None, "quote": None}},
    "announcement_no": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "hedge": {
    "underlying_commodities": {"value": [], "evidence": {"page": None, "quote": None}},
    "hedge_object_category": {"value": ["Unknown"], "evidence": {"page": None, "quote": None}},
    "exposure_direction": {"value": "Unknown", "evidence": {"page": None, "quote": None}},
    "exposure_basis_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "purpose_one_sentence": {"value": None, "evidence": {"page": None, "quote": None}},
    "limits_basis_text": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "trading": {
    "instruments": {"value": [], "evidence": {"page": None, "quote": None}},
    "venues": {"value": [], "evidence": {"page": None, "quote": None}},
    "venue_scope_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "venue_scope_flags": {"value": {"exchange_only": None, "no_otc": None, "no_overseas": None, "domestic_only": None},
                          "evidence": {"page": None, "quote": None}}
  },
  "limits": {
    "recyclable": {"value": None, "evidence": {"page": None, "quote": None}},
    "margin_total": {"value": None, "evidence": {"page": None, "quote": None}},
    "premium_total": {"value": None, "evidence": {"page": None, "quote": None}},
    "max_contract_value": {"value": None, "evidence": {"page": None, "quote": None}},
    "margin_cash": {"value": None, "evidence": {"page": None, "quote": None}},
    "margin_collateral": {"value": None, "evidence": {"page": None, "quote": None}},
    "credit_occupy": {"value": None, "evidence": {"page": None, "quote": None}},
    "emergency_margin": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "validity": {
    "auth_months": {"value": None, "evidence": {"page": None, "quote": None}},
    "single_order_rolling": {"value": None, "evidence": {"page": None, "quote": None}},
    "auth_start_trigger": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "funding": {
    "funding_source": {"value": [], "evidence": {"page": None, "quote": None}},
    "prohibit_bank_credit": {"value": None, "evidence": {"page": None, "quote": None}},
    "prohibit_raised_funds": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "governance": {
    "board_meeting_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "audit_committee_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "shareholders_meeting_required": {"value": None, "evidence": {"page": None, "quote": None}},
    "is_related_party_transaction": {"value": None, "evidence": {"page": None, "quote": None}},
    "needs_related_party_vote": {"value": None, "evidence": {"page": None, "quote": None}},
    "management_authorized": {"value": None, "evidence": {"page": None, "quote": None}},
    "board_vote_unanimous": {"value": None, "evidence": {"page": None, "quote": None}},
    "policy_docs": {"value": [], "evidence": {"page": None, "quote": None}}
  },
  "disclaimer": {
    "non_speculation": {"value": None, "evidence": {"page": None, "quote": None}},
    "risk_level_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "investor_warning_text": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "risk": {
    "risk_items": [],
    "risk_types": {"value": [], "evidence": {"page": None, "quote": None}}
  },
  "controls": {
    "control_items": [],
    "control_tags": {"value": [], "evidence": {"page": None, "quote": None}}
  },
  "impact": {
    "benefit_text": {"value": None, "evidence": {"page": None, "quote": None}}
  },
  "sponsor": {
    "opinion_text": {"value": None, "evidence": {"page": None, "quote": None}},
    "compliance_basis_refs": {"value": [], "evidence": {"page": None, "quote": None}}
  },
  "attachments": [],
  "notes": {
    "missing_fields": [],
    "structure_warnings": []
  }
}

# Deepseek_prompt(抽取)
SYSTEM_DEEPSEEK_EXTRACT = (
    "你是上市公司商品套期保值公告的信息抽取助手。"
    "只从原文抽取，不允许编造。"
    "输出必须是严格JSON（只输出JSON）。"
)

def build_prompt_deepseek_extract(doc_text: str) -> str:
    schema_str = json.dumps(SCHEMA, ensure_ascii=False, indent=2)
    return f"""
请按 schema 输出一个严格JSON对象，字段必须与 schema 完全一致，不允许新增键，不允许缺失键。
严禁输出任何带点的键名（例如 'hedge.hedge_object' 这种一律禁止）——只能按嵌套对象表达。
如果公告未披露某字段：在 notes.missing_fields 里补一条 {{field, status}}，status 只能取：
- NOT_DISCLOSED（公告未披露）
- NOT_APPLICABLE（确实不适用）
- EXTRACTION_FAILED（原文有但你没抽到）

证据 evidence 规则（必须遵守）：
- evidence 必须是对象：{{"page":页码(int), "quote":"原文短句"}}；quote尽量短，但要能支撑字段。

枚举约束（必须遵守）：
- trading.instruments.value 只能取：["期货","期权","远期","掉期","其他"]
- hedge.hedge_object_category.value 只能取：["原材料","产品","库存","订单","其他","Unknown"] 且禁止空数组
- hedge.exposure_direction.value 只能取：["采购成本暴露","销售价格暴露","Unknown"]
编号列表（请尽量抽满，保留信息密度）：
- risk.risk_items：按公告编号1、2、3…分别抽出，每条带 no/type_norm/text/evidence
- controls.control_items：按公告编号1、2、3…分别抽出，每条带 no/tags/text/evidence

特别要补的“容易漏但很重要”的点：
- 关联交易/无需关联表决程序、授权经理层、全票通过（治理强度）
- 非投机声明/风险等级/特别风险提示（单列到 disclaimer）
- 保证金上限的确定依据（产量计划/保证金规则）
- “不使用募集资金或银行信贷”以及“不得超过批准额度”等硬约束（control_items tags里标注）
- 影响段 benefit_text、备查文件 attachments、保荐合规依据 compliance_basis_refs

schema：
{schema_str}

公告原文（按页）：
{doc_text}
""".strip()


# 结构修复：删除含点键
def drop_dotted_keys(obj: dict) -> dict:
    if not isinstance(obj, dict):
        return obj
    warnings = obj.get("notes", {}).get("structure_warnings", [])
    for k in list(obj.keys()):
        if "." in k:
            warnings.append(f"删除非法键（含点路径污染）：{k}")
            obj.pop(k, None)
    if "notes" in obj and isinstance(obj["notes"], dict):
        obj["notes"]["structure_warnings"] = warnings
    return obj


# Qwen_prompt(清洗)
SYSTEM_QWEN_NORM_PATCH = (
    "你是金融数据清洗专家。你的任务是输出用于修正原始数据的‘补丁数据’。"
    "针对日期、金额、枚举值进行标准化。如果原文数据无法解析，保持 null。"
    "严禁补充新事实，不要改变原文的含义"
    "输出必须是严格 JSON（只输出JSON）。"
)


def build_prompt_qwen_norm_patch(ds_json: dict) -> str:
    ds_str = json.dumps(ds_json, ensure_ascii=False)
    patch_schema = {
        "meta": {
            "announcement_date": "YYYY-MM-DD (ISO格式)"
        },
        "validity": {
            "auth_months": "12(填整数，若无法提取填null)"
        },
        "limits": {
            "margin_total": "清洗后的金额数值(单位元)",
            "premium_total": "清洗后的金额数值(单位元)",
            "max_contract_value": "清洗后的金额数值(单位元)"
        },
        "trading": {
            "instruments": []
        },
        "hedge": {
            "underlying_commodities": []
        }
    }

    return f"""
请分析输入的 DeepSeek JSON 数据，生成一个“补丁对象”。
Python 脚本将使用你的输出，直接覆盖原始 JSON 中的对应 value 字段。

清洗规则：
1. **日期 (meta.announcement_date)**: 转为 "YYYY-MM-DD(ISO格式)"。
2. **月份 (validity.auth_months)**: 转成整数月数（12个月/十二个月/12 → 12），识别不了填 null。
3. **金额 (limits.*)**: 将所有金额统一转换为 **“元”** 为单位的数值（Float），保留2位小数。
   - 输入: "70,000万元" -> 输出: 700000000.00
   - 输入: "5亿元" -> 输出: 500000000.00
   - 如果无法计算，输出 null。
4. **工具 (trading.instruments)**: 归一化到枚举 ["期货","期权","远期","掉期","其他"]。
5. **品种 (hedge.underlying_commodities)**: 在知识库里检索，对照元素周期表，规范化。
   -如 "铜"->"铜Cu"，"金"->"金Au","银"->"银Ag"……

重要：结构必须与下方 schema 完全一致，**只输出需要修改的字段**。如果某个字段原数据为空且无法清洗，输出 null。

Patch Schema:
{json.dumps(patch_schema, ensure_ascii=False, indent=2)}

待清洗数据 (DeepSeek):
{ds_str}
""".strip()

def apply_qwen_patch(original_data: dict, patch_data: dict) -> dict:

    patched = copy.deepcopy(original_data)

    # 1. Meta Date
    if patch_data.get("meta", {}).get("announcement_date"):
        patched["meta"]["announcement_date"]["value"] = patch_data["meta"]["announcement_date"]

    # 2. Validity Months
    if patch_data.get("validity", {}).get("auth_months"):
        patched["validity"]["auth_months"]["value"] = patch_data["validity"]["auth_months"]

    # 3. Limits (金额清洗覆盖)
    patch_limits = patch_data.get("limits", {})
    for field in ["margin_total", "premium_total", "max_contract_value"]:
        new_val = patch_limits.get(field)
        if new_val is not None:
            patched["limits"][field]["value"] = new_val

    # 4. Trading Instruments
    if patch_data.get("trading", {}).get("instruments"):
        patched["trading"]["instruments"]["value"] = patch_data["trading"]["instruments"]

    # 5. Hedge Commodities
    if patch_data.get("hedge", {}).get("underlying_commodities"):
        patched["hedge"]["underlying_commodities"]["value"] = patch_data["hedge"]["underlying_commodities"]

    return patched

# Qwen_prompt(验证)
SYSTEM_QWEN_VALIDATE = (
    "你是套期保值公告结构化抽取结果的质量审计员。"
    "你只做核验与打分：不允许改写或补充 DeepSeek 的抽取内容。"
    "输出必须是严格JSON（只输出JSON）。"
)

def build_prompt_qwen_validate(doc_text: str, ds_json: dict) -> str:
    ds_str = json.dumps(ds_json, ensure_ascii=False)

    validation_schema = {
        "validation": {
            "field_checks": [
                # {field_path, verdict:"PASS/FAIL/UNCERTAIN", reason, page_hint}
            ],
            "consistency_checks": [
                # {check, verdict:"PASS/FAIL/UNCERTAIN", reason}
            ],
            "scores": {
                "coverage_score_0_100": None,
                "evidence_score_0_100": None,
                "consistency_score_0_100": None,
                "overall_score_0_100": None
            },
            "top_issues": [],
            "suggest_patch": [
                {
                    "path": "meta.announcement_date.value",
                    "patch_type": "FORMAT",  # 或 "EXTRACT"
                    "value": "2024-01-01",
                    "reason": "原文日期格式标准化",
                    "evidence": {"page": 1, "quote": "..."}
                }
            ]
        }
    }

    return f"""
你将看到：公告原文（按页）+ DeepSeek抽取JSON。请完成“质量核验”，输出 validation 对象。

硬性规则：
1) 你只能核验、打分、指出问题；不得改写 ds_json。
2) field_checks 只核验“高价值字段”（建议至少覆盖以下路径）：
   meta.company_name.value
   meta.announcement_date.value
   trading.instruments.value
   trading.venue_scope_text.value
   limits.margin_total.value
   validity.auth_months.value
   funding.prohibit_bank_credit.value
   funding.prohibit_raised_funds.value
   sponsor.opinion_text.value
3) 每条 field_checks 都要给 verdict（PASS/FAIL/UNCERTAIN）与原因，并给 page_hint（若能判断）
4) consistency_checks 至少做3类一致性核验（结合原文语言理解）：
   - 场所范围（仅交易所/不场外/不境外）与工具类型（远期/掉期）是否矛盾
   - 资金来源限制（不使用信贷/募集资金）与是否出现授信占用/保证金来源描述是否矛盾
   - missing_fields 是否“看起来其实在原文提到了”（用关键词判断即可；不确定就 UNCERTAIN）
5) scores 给 0~100 分，overall 需结合前三项分数与问题严重性综合给出。
6) suggest_patch规则：
   - 如果是格式错误（如日期格式），patch_type 填 "FORMAT"。
   - 如果是漏抽（原值为Unknown/null但原文有），patch_type 填 "EXTRACT"。
   - value 必须是你可以确定的修正值。
   - path 必须是准确的 JSON 路径。
   - 如果没有明确修改建议，suggest_patch 留空数组。

输出必须严格符合 schema：
{json.dumps(validation_schema, ensure_ascii=False, indent=2)}

公告原文：
{doc_text}

DeepSeek JSON：
{ds_str}
""".strip()

PATCH_PATH_WHITELIST = {
    "meta.announcement_date.value",
    "trading.instruments.value",
    "trading.venue_scope_text.value",
    "limits.margin_total.value",
    "validity.auth_months.value",
    "funding.prohibit_bank_credit.value",
    "funding.prohibit_raised_funds.value",
    "sponsor.opinion_text.value",
}
def set_by_dot_path(root: dict, path: str, value):
    keys = path.split(".")
    cur = root
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value

def get_by_dot_path(root: dict, path: str):
    cur = root
    for k in path.split("."):
        cur = cur[k]
    return cur

def apply_validation_patches(ds_json: dict, validation: dict, auto_fix: bool = False) -> dict:

    patched = copy.deepcopy(ds_json)
    if not auto_fix:
        return patched

    for p in (validation.get("suggest_patch") or []):
        path = p.get("path")
        if path not in PATCH_PATH_WHITELIST:
            continue

        ptype = p.get("patch_type")
        val = p.get("value")

        if ptype == "FORMAT":
            set_by_dot_path(patched, path, val)

        elif ptype == "EXTRACT":
            ev = p.get("evidence") or {}
            if not (ev.get("quote") and ev.get("page") is not None):
                continue

            try:
                cur_val = get_by_dot_path(patched, path)
            except Exception:
                cur_val = None
            if cur_val in (None, "Unknown", [], ""):
                set_by_dot_path(patched, path, val)

    return patched

# Qwen_prompt(汉化)
SYSTEM_QWEN_TRANS = "你是资深的金融数据分析师。你的任务是将JSON数据的结构完全汉化，使其符合中国金融行研报告的阅读习惯。"

def build_prompt_qwen_trans(full_data: dict) -> str:
    data_str = json.dumps(full_data, ensure_ascii=False)

    return f"""
任务：请将下方 JSON 对象中 **所有的键名（Keys）** 从英文翻译成中文。

### 核心原则（必须遵守）：
1. **深度递归**：不要只翻译第一层！必须遍历每一个嵌套对象，把诸如 "evidence", "page", "quote", "value" 等底层键全部翻译。
2. **值不变**：严禁修改任何 Value（值）的内容，只改 Key（键）。
3. **专业性**：使用标准的金融行研术语。

### 翻译参考示例（请学习此风格并应用到其他字段）：

**【通用结构字段】** (遇到这些词一律按此翻译)：
- "value"    -> "内容" 或 "数值"
- "evidence" -> "证据来源"
- "page"     -> "页码"
- "quote"    -> "原文摘录"
- "items"    -> "明细列表"
- "notes"    -> "备注信息"

**【专业业务字段】** (举一反三)：
- "meta" -> "基本信息"
- "hedge" -> "套保方案概况"
- "underlying_commodities" -> "套保标的物"
- "limits" -> "额度与资金限制"
- "margin_total" -> "保证金总额"
- "credit_occupy" -> "授信占用"
- "validity" -> "决议有效期"
- "controls" -> "风控体系"
- "normalized" -> "结构化清洗数据"

请发挥你的专业能力，将示例中未列出的其他英文键（如 exposure_direction, instruments, venue_scope_flags 等）根据上下文准确翻译成中文。

### 待处理 JSON：
{data_str}
""".strip()


# 主流程：输出4份文件
def main(api_key=None, model_settings=None, pdf_dir=None, out_dir=None):
    global API_KEY, MODEL_DEEPSEEK, MODEL_QWEN_NORM, MODEL_QWEN_VALIDATE, MODEL_QWEN_TRANS, PDF_DIR, OUT_DIR
    
    # 动态注入后端传入的API Key与模型配置
    if api_key:
        API_KEY = api_key
    if model_settings:
        # 模型名字对应 a/b/c/d 等（由后端映射，也可以直接传字母对应的真实模型名）
        # 1.分析模型
        if 'analysis' in model_settings: MODEL_DEEPSEEK = model_settings['analysis']
        # 2.数据处理模型
        if 'processing' in model_settings: MODEL_QWEN_NORM = model_settings['processing']
        # 3.recheck-llm
        if 'recheck' in model_settings: MODEL_QWEN_VALIDATE = model_settings['recheck']
        # 4.翻译模型
        if 'translation' in model_settings: MODEL_QWEN_TRANS = model_settings['translation']
    if pdf_dir:
        PDF_DIR = pdf_dir
    if out_dir:
        OUT_DIR = out_dir

    os.makedirs(OUT_DIR, exist_ok=True)

    pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    total_files = len(pdf_files)
    if not pdf_files:
        raise ValueError(f"目录 {PDF_DIR} 下没有找到PDF。请把公告PDF放进去。")
    print(f"目录中检索到{total_files}个pdf文件\n")
    for index,pdf_path in enumerate(pdf_files,1):
        file_name = os.path.basename(pdf_path)
        base = os.path.splitext(file_name)[0]
        if ":" in base or "：" in base:
            if "：" in base:
                colon_pos = base.index("：")
            else:
                colon_pos = base.index(":")
            name = base[:colon_pos]
        else:
            name = base[:4]
        print(f"[{index}/{total_files}] 正在读取并解析pdf文本：{file_name}")
        doc_text = pdf_to_text_by_page(pdf_path)

        # (1) DeepSeek 抽取
        print("正在调用Deepseek V3.2 进行信息结构化，约1min")
        ds = llm_json(MODEL_DEEPSEEK, SYSTEM_DEEPSEEK_EXTRACT, build_prompt_deepseek_extract(doc_text))
        ds = drop_dotted_keys(ds)

        # 输出:DeepSeek 原始抽取
        print("正在生成Deepseek结构化文档，详见文件夹out_txt(下同)")
        raw_path = os.path.join(OUT_DIR, f"{name}__deepseek_raw.txt")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(ds, ensure_ascii=False, indent=2))

        # (2) Qwen 清洗
        print("正在调用qwen-plus进行格式清洗")
        qwen_norm = llm_json(MODEL_QWEN_NORM, SYSTEM_QWEN_NORM_PATCH, build_prompt_qwen_norm_patch(ds))
        patch_data = qwen_norm
        patched = apply_qwen_patch(ds,patch_data)

        # (3) Qwen 验证+自动修正
        print("正在调用qwen-max验证抽取信息")
        if ENABLE_VALIDATION:
            qwen_val = llm_json(MODEL_QWEN_VALIDATE, SYSTEM_QWEN_VALIDATE, build_prompt_qwen_validate(doc_text, patched))
            validation = (qwen_val.get("validation") or {})
            val_path = os.path.join(OUT_DIR, f"{name}__3_qwen_validation.txt")
            print("正在生成验证信息评审报告")
            with open(val_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(validation, ensure_ascii=False, indent=2))
            patched["validation_qwen"] = validation
            patched = apply_validation_patches(patched, validation, auto_fix=AUTO_FIX_FROM_VALIDATION)
        print("正在生成最终报告")
        # 输出:Qwen 清洗覆盖后的 JSON
        patched_path = os.path.join(OUT_DIR, f"{name}__qwen_patched.txt")
        with open(patched_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(patched, ensure_ascii=False, indent=2))
        # 输出:Qwen 汉化版
        cn_data = llm_json(MODEL_QWEN_TRANS, SYSTEM_QWEN_TRANS, build_prompt_qwen_trans(patched))
        CN_path = os.path.join(OUT_DIR, f"{name}__qwen_patched_CN.txt")
        with open(CN_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(cn_data, ensure_ascii=False, indent=2))

        print(f"{base} 处理完毕\n")

    print("全部处理完成")

if __name__ == "__main__":
    API_KEY = input("输入您自己的APIKEY(阿里云百炼）: ")
    main()
    input("程序运行结束.")