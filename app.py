import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
# 環境変数からAPIキーを読み込むことで、セキュリティを確保
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flaskアプリケーションの初期化
app = Flask(__name__)

# ルートURL（/）にアクセスしたときに表示されるページ
@app.route('/')
def index():
    # templatesフォルダ内のindex.htmlをレンダリングして表示
    return render_template('index.html')

# プロンプト生成APIエンドポイント
@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    # リクエストボディからユーザーの入力（user_input）を取得
    user_input = request.json.get('user_input')

    # 入力がない場合はエラーを返す
    if not user_input:
        return jsonify({'error': '入力がありません。具体的なイメージを入力してください。'}), 400

    try:
        # --- ここがAIへの指示（プロンプトエンジニアリングの肝！）---
        # あなたの差別化ポイントを反映させる重要な部分です。
        # 初心者の曖昧な表現を高品質なプロンプトに変換するようAIに指示します。
        prompt_for_ai = f"""
        # ... (中略) ...

    あなたは、画像生成AI（MidjourneyやStable Diffusionなど）のプロンプトを専門とするエキスパートです。
    以下のユーザーが入力した日本語のイメージを、高品質な画像を生成するための詳細かつ効果的な**日本語の**ポジティブプロンプトとネガティブプロンプトに変換してください。
    ユーザーは画像生成AIの初心者であり、曖昧な表現で入力する可能性がありますが、あなたはそれを具体的かつプロフェッショナルなプロンプトに拡張してください。
    光の当たり方、構図、画風、質感、感情表現、カメラアングルなど、画像生成AIで効果的な詳細描写を積極的に加えてください。
    また、一般的な失敗を防ぐためのネガティブプロンプトも必ず含めてください。

    イメージ:「{user_input}」

    以下のフォーマットで出力してください：
    ポジティブプロンプト（日本語）: [ここに生成されたポジティブプロンプト]
    ネガティブプロンプト（日本語）: [ここに生成されたネガティブプロンプト]
    """

        # ... (中略) ...

        # OpenAI APIを呼び出してプロンプトを生成
        # modelは、gpt-4o-mini, gpt-3.5-turbo, gpt-4o などから選択できます。
        # まずはコスト効率の良い gpt-4o-mini から試すのがおすすめです。
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # ここを 'gpt-3.5-turbo' や 'gpt-4o' に変更できます
            messages=[
                # システムプロンプト：AIの役割を設定
                {"role": "system", "content": "You are a helpful assistant that generates detailed image generation prompts."},
                # ユーザープロンプト：ユーザーの要求とAIへの詳細な指示
                {"role": "user", "content": prompt_for_ai}
            ],
            temperature=0.7, # 応答の創造性を制御（0.0-1.0, 高いほど創造的）
            max_tokens=500 # 生成される応答の最大トークン数
        )

        # AIの応答内容を取得
        ai_response_content = completion.choices[0].message.content

        # AIの応答からポジティブプロンプトとネガティブプロンプトを抽出
        positive_prompt = "生成できませんでした。AIの応答形式が不正な可能性があります。"
        negative_prompt = "生成できませんでした。AIの応答形式が不正な可能性があります。"

        lines = ai_response_content.split('\n')
        for line in lines:
            if line.startswith('ポジティブプロンプト（日本語）:'): # <-- ここを修正
                positive_prompt = line.replace('ポジティブプロンプト（日本語）:', '').strip() # <-- ここを修正
            elif line.startswith('ネガティブプロンプト（日本語）:'): # <-- ここを修正
                negative_prompt = line.replace('ネガティブプロンプト（日本語）:', '').strip() # <-- ここを修正
        # 生成されたプロンプトをJSON形式でクライアントに返す
        return jsonify({
            'positive_prompt': positive_prompt,
            'negative_prompt': negative_prompt
        })

    except Exception as e:
        # エラーが発生した場合の処理
        print(f"Error generating prompt: {e}") # サーバー側のログに出力
        return jsonify({'error': 'プロンプトの生成中にエラーが発生しました。時間を置いて再度お試しください。'}), 500

# アプリケーションを開発モードで実行（デバッグ情報が表示される）
if __name__ == '__main__':
    app.run(debug=True)