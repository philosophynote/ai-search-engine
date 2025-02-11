from pydantic import BaseModel, field_validator

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
    capital: str
    number_of_employees: int
    phone_number: str
    source_urls: list[str]

    @field_validator("number_of_employees", mode="before")
    def remove_commas(cls, v):
        if isinstance(v, str):
            try:
                return int(v.replace(",", ""))
            except ValueError:
                raise ValueError(f"Invalid number for number_of_employees: {v}")
        return v
