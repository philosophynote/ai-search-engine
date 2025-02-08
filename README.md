# 企業特定検索

詳細を知りたい企業名を送信すると企業名をWEBで検索して
結果を返してくれます

返却される内容
- 企業名（法人格込み）
- フリガナ
- 法人番号
- 所在地
- 代表者名
- 役員名（複数）
- 企業URL
- 企業が提供しているサービスのLP
- 業種
- 設立年月日
- 資本金
- 従業員数
- 電話番号
- 情報元URL一覧

同名の企業があり、候補が複数ある場合は
全て返却されます

## レスポンスJSON設計

```json
{
  [
  "company_name": "string",
  "furigana": "string",
  "corporate_number": "string",
  "location": "string",
  "representative_name": "string",
  "officer_names": ["string"],
  "company_url": "string",
  "service_url": "string",
  "industry": "string",
  "establishment_date": "string",
  "capital": "number",
  "number_of_employees": "number",
  "phone_number": "string",
  "source_urls": ["string"]
  ]
}
```

同名の企業があり、候補が複数ある場合は、上記のJSONオブジェクトが配列として返却されます。

## 例

質問文

「東京都新宿区にあるアラームボックスについて調べて」

回答

```json
{
  [
  "company_name": "アラームボックス株式会社",
  "furigana": "アラームボックスカブシキガイシャ",
  "corporate_number": "7011101077374",
  "location": "東京都新宿区市谷本村町3-22 ナカバビル8F",
  "representative_name": "武田 浩和",
  "officer_names": ["具志堅 功太郎","伊藤 貴博","菊池 聡"],
  "company_url": "https://alarmbox.co.jp",
  "service_url": "https://alarmbox.jp",
  "industry": "ソフトウェア・情報処理",
  "establishment_date": "2016/6/1",
  "capital": "336000000",
  "number_of_employees": "47",
  "phone_number": "03-6261-0351",
  "source_urls": [
    "https://alarmbox.co.jp/",
    "https://alarmbox.co.jp/about-new/",
    "https://mid-tenshoku.com/agency/a-9940/"
  ]
  ]
}