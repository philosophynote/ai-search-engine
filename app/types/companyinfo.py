from pydantic import BaseModel, field_validator
from typing import Optional
import re


class CompanyInfo(BaseModel):
    company_name: str
    furigana: str
    corporate_number: str
    location: str
    representative_name: str
    officer_names: list[str]
    company_url: str
    service_url: str
    industry: str
    establishment_date: str
    capital: int  # 型を str から int に変更
    number_of_employees: int = 0  # None 対応として default 値を設定
    phone_number: str = ""  # None 対応として default 値を設定
    source_urls: list[str]

    @field_validator("number_of_employees", mode="before")
    def remove_commas(cls, v):
        if v is None:
            return 0
        if isinstance(v, str):
            try:
                return int(v.replace(",", ""))
            except ValueError:
                raise ValueError(f"Invalid number for number_of_employees: {v}")
        return v

    @field_validator("phone_number", mode="before")
    def default_phone_number(cls, v):
        if v is None:
            return ""
        return v

    # @field_validator("capital", mode="before")
    # def parse_capital(cls, v):
    #     if isinstance(v, str):
    #         # 数字以外の文字を除去してから整数に変換
    #         numbers = re.sub(r"\D", "", v)
    #         return int(numbers) if numbers else 0
    #     return v
