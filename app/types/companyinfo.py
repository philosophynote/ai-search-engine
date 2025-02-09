from pydantic import BaseModel

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
