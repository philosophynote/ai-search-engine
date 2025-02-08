# ベースイメージとして公式Pythonイメージを使用（必要に応じて他のイメージに変更可能）
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 全てのファイルをコンテナにコピー
COPY . .

# FastAPIおよびStreamlitで使用するポートを公開
EXPOSE 8000 8501

# デフォルトの実行コマンド（docker-composeで上書き可能）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
