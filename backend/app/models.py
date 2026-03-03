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
