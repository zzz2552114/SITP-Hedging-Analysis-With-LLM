from tortoise import fields, models

class ListedCompanyBase(models.Model):
    stock_code = fields.CharField(max_length=6, primary_key=True)
    company_name = fields.CharField(max_length=100)
    company_short_name = fields.CharField(max_length=50)
    market = fields.CharField(max_length=20, db_index=True)
    establish_date = fields.DateField(null=True)
    list_date = fields.DateField(null=True)

    class Meta:
        table = "listed_company_base"


class CompanyYearlyMainBusiness(models.Model):
    id = fields.IntField(primary_key=True)
    stock_code = fields.ForeignKeyField("models.ListedCompanyBase", related_name="yearly_businesses", to_field="stock_code", db_constraint=True)
    biz_year = fields.SmallIntField(db_index=True)
    main_business = fields.TextField()
    industry_class = fields.CharField(max_length=50, db_index=True)
    business_core = fields.CharField(max_length=200, db_index=True)

    class Meta:
        table = "company_yearly_main_business"
        unique_together = (("stock_code", "biz_year"),)


class FuturesCommodityCatalog(models.Model):
    catalog_id = fields.IntField(primary_key=True)
    parent_catalog = fields.ForeignKeyField("models.FuturesCommodityCatalog", related_name="children", null=True)
    catalog_level = fields.SmallIntField(db_index=True)
    commodity_full_name = fields.CharField(max_length=100, unique=True)
    commodity_short_name = fields.CharField(max_length=50)
    exchange = fields.CharField(max_length=50, null=True)
    association_code = fields.CharField(max_length=50, null=True, unique=True)

    class Meta:
        table = "futures_commodity_catalog"


class AnnouncementMeta(models.Model):
    announcement_id = fields.CharField(max_length=50, primary_key=True)
    stock_code = fields.ForeignKeyField("models.ListedCompanyBase", related_name="announcements", to_field="stock_code", db_constraint=True)
    announcement_title = fields.CharField(max_length=200)
    publish_date = fields.DateField(db_index=True)
    biz_year = fields.SmallIntField()
    storage_type = fields.CharField(max_length=20) # local/minio/other
    storage_key = fields.CharField(max_length=500) # relative path bounds to `e:/sitp-web/data/pdfs` for example
    parse_status = fields.SmallIntField(db_index=True, default=0) # 0:未解析, 1:成功, 2:失败
    parsed_at = fields.DatetimeField(null=True)
    parse_error = fields.CharField(max_length=500, null=True)
    parse_version = fields.CharField(max_length=50, null=True)

    class Meta:
        table = "announcement_meta"
        indexes = (
            ("stock_code", "biz_year"),
        )


class HedgingBusinessDetail(models.Model):
    id = fields.IntField(primary_key=True)
    announcement = fields.ForeignKeyField("models.AnnouncementMeta", related_name="hedging_details", to_field="announcement_id", db_constraint=True)
    stock_code = fields.ForeignKeyField("models.ListedCompanyBase", related_name="hedging_records", to_field="stock_code", db_constraint=True)
    catalog = fields.ForeignKeyField("models.FuturesCommodityCatalog", related_name="hedging_records", to_field="catalog_id", db_constraint=True)
    biz_year = fields.SmallIntField()
    hedging_limit = fields.DecimalField(max_digits=20, decimal_places=2, null=True) # 单位:万元
    hedging_direction = fields.CharField(max_length=20, null=True)
    hedging_term = fields.CharField(max_length=50, null=True)
    business_desc = fields.TextField(null=True)

    class Meta:
        table = "hedging_business_detail"
        unique_together = (("announcement_id", "catalog_id", "biz_year", "hedging_direction"),)
        indexes = (
            ("stock_code", "biz_year"),
            ("catalog_id", "biz_year"),
        )


class AnnouncementParseResult(models.Model):
    id = fields.BigIntField(primary_key=True)
    announcement = fields.ForeignKeyField("models.AnnouncementMeta", related_name="raw_parse_results", null=True, to_field="announcement_id", db_constraint=True)
    llm_model = fields.CharField(max_length=50, null=True)
    prompt_version = fields.CharField(max_length=50, null=True)
    parsed_json = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "announcement_parse_result"


class FuturesContract(models.Model):
    """期货合约品种主表，存放从 Tushare 获取的所有可交易合约"""
    ts_code = fields.CharField(max_length=20, primary_key=True)   # e.g. CU2501.SHF
    symbol = fields.CharField(max_length=10, db_index=True)       # e.g. CU
    name = fields.CharField(max_length=50, db_index=True)         # e.g. 沪铜2501
    exchange = fields.CharField(max_length=10, db_index=True)     # SHFE/DCE/CZCE/CFFEX/INE/GFEX
    fut_code = fields.CharField(max_length=10, db_index=True)     # 品种代码 e.g. CU
    pinyin_initial = fields.CharField(max_length=1, db_index=True, default='')  # 品种首字母，供前端分组
    list_date = fields.CharField(max_length=8, null=True)
    delist_date = fields.CharField(max_length=8, null=True)

    class Meta:
        table = "futures_contract"


class FuturesDailyKline(models.Model):
    """期货日K线数据"""
    id = fields.BigIntField(primary_key=True)
    ts_code = fields.ForeignKeyField("models.FuturesContract", related_name="klines", to_field="ts_code", db_constraint=True)
    trade_date = fields.CharField(max_length=8, db_index=True)  # YYYYMMDD
    pre_close = fields.FloatField(null=True)
    pre_settle = fields.FloatField(null=True)
    open = fields.FloatField(null=True)
    high = fields.FloatField(null=True)
    low = fields.FloatField(null=True)
    close = fields.FloatField(null=True)
    settle = fields.FloatField(null=True)
    change1 = fields.FloatField(null=True)   # 涨跌1 (收盘价-昨结算价)
    change2 = fields.FloatField(null=True)   # 涨跌2 (收盘价-昨收盘价)
    vol = fields.FloatField(null=True)       # 成交量(手)
    amount = fields.FloatField(null=True)    # 成交金额(万元)
    oi = fields.FloatField(null=True)        # 持仓量(手)
    oi_chg = fields.FloatField(null=True)    # 持仓变化

    class Meta:
        table = "futures_daily_kline"
        unique_together = (("ts_code", "trade_date"),)
        indexes = (
            ("ts_code", "trade_date"),
        )
