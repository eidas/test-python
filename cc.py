import argparse
import sys
import os
import subprocess

# --- AI Integration (requires Google API Key) ---
try:
    import google.generativeai as genai
except ImportError:
    print("エラー: Gemini APIライブラリがありません。", file=sys.stderr)
    print("pip install google-generativeai を実行してください。", file=sys.stderr)
    sys.exit(1)

# --- Conversation History ---
conversation_history = []

def add_to_history(role, text):
    """会話履歴に新しいエントリーを追加する"""
    conversation_history.append({"role": role, "parts": [text]})

# --- Command Handlers ---

def handle_ask(args):
    """AIに質問し、会話履歴を更新する"""
    # APIキーの設定 (環境変数から取得)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("エラー: 環境変数 GEMINI_API_KEY が設定されていません。", file=sys.stderr)
        print("APIキーを設定してから再実行してください。", file=sys.stderr)
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    print("AIと思考中...\n")
    try:
        # 会話履歴をコンテキストとして使用
        chat = model.start_chat(history=conversation_history)
        response = chat.send_message(args.prompt)

        ai_response = response.text
        print("--- Gemini ---")
        print(ai_response)
        print("--------------")

        # 履歴を更新
        add_to_history("user", args.prompt)
        add_to_history("model", ai_response)

    except Exception as e:
        print(f"エラー: AIとの通信に失敗しました: {e}", file=sys.stderr)

def handle_read(args):
    """ファイルを読み込み、その内容を会話履歴に追加する"""
    try:
        with open(args.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_context = f"ファイル「{args.filepath}」を読み込みました。内容は以下の通りです。\n\n---\n{content}\n---"
        add_to_history("user", file_context)
        print(f"ファイルを読み込み、AIのコンテキストに追加しました: {args.filepath}")

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {args.filepath}", file=sys.stderr)
    except Exception as e:
        print(f"エラー: ファイルを読み込めませんでした: {e}", file=sys.stderr)

def handle_write(args):
    try:
        dir_path = os.path.dirname(args.filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(args.filepath, 'w', encoding='utf-8') as f:
            f.write(args.content)
        print(f"ファイルに書き込みました: {args.filepath}")
    except Exception as e:
        print(f"エラー: ファイルに書き込めませんでした: {e}", file=sys.stderr)

def handle_ls(args):
    try:
        path = args.path
        if not os.path.exists(path):
            print(f"エラー: パスが見つかりません: {path}", file=sys.stderr)
            return
        
        print(f"--- {os.path.abspath(path)} の一覧 ---")
        for item in os.listdir(path):
            print(item)
        print("--- 一覧ここまで ---")
    except Exception as e:
        print(f"エラー: ファイル一覧を取得できませんでした: {e}", file=sys.stderr)

def handle_run(args):
    print(f"$ {args.command}")
    try:
        result = subprocess.run(args.command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print("--- 標準出力 ---")
            print(result.stdout.strip())
        if result.stderr:
            print("--- 標準エラー出力 ---")
            print(result.stderr.strip())
    except subprocess.CalledProcessError as e:
        print(f"エラー: コマンドの実行に失敗しました (終了コード: {e.returncode})", file=sys.stderr)
        if e.stdout:
            print(e.stdout.strip(), file=sys.stderr)
        if e.stderr:
            print(e.stderr.strip(), file=sys.stderr)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)

def handle_commit(args):
    print("GitコミットをAIで支援します...")
    print("（この機能はステップ4で実装します）")

def main():
    parser = argparse.ArgumentParser(
        prog="cc",
        description="AIコーディングアシスタント Gemini Coder",
        epilog="使いたいサブコマンドを指定してください。例: cc ask \"Hello WorldをPythonで\""
    )
    subparsers = parser.add_subparsers(title="サブコマンド", dest="command", required=True)

    # ask コマンド
    parser_ask = subparsers.add_parser("ask", help="AIに質問、コード生成などを依頼する")
    parser_ask.add_argument("prompt", type=str, help="AIへの指示や質問内容")
    parser_ask.set_defaults(func=handle_ask)

    # read コマンド
    parser_read = subparsers.add_parser("read", help="ファイルの内容を読み込む")
    parser_read.add_argument("filepath", type=str, help="読み込むファイルのパス")
    parser_read.set_defaults(func=handle_read)

    # write コマンド
    parser_write = subparsers.add_parser("write", help="ファイルに内容を書き込む")
    parser_write.add_argument("filepath", type=str, help="書き込むファイルのパス")
    parser_write.add_argument("content", type=str, help="書き込む内容")
    parser_write.set_defaults(func=handle_write)

    # ls コマンド
    parser_ls = subparsers.add_parser("ls", help="ファイルやディレクトリの一覧を表示する")
    parser_ls.add_argument("path", type=str, nargs='?', default='.', help="一覧表示するディレクトリのパス")
    parser_ls.set_defaults(func=handle_ls)

    # run コマンド
    parser_run = subparsers.add_parser("run", help="シェルコマンドを実行する")
    parser_run.add_argument("command", type=str, help="実行するシェルコマンド")
    parser_run.set_defaults(func=handle_run)

    # commit コマンド
    parser_commit = subparsers.add_parser("commit", help="AI支援によるGitコミット")
    parser_commit.set_defaults(func=handle_commit)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
