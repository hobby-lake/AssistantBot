# SUMMARY
Discordのサーバー管理アシスタントです。  
基本オーダーメイドで構築していこうと思っています。  
このBotは「TAKUYURI COMMUNITY」に最適化されています。
使用登録がBot側で為されているサーバーのみ使用可能です。

# ENVIRONMENT
- Windows11 24H2(テスト環境)
- ConoHa VPS 1GBRAM/2CoreCPU
- Ubuntu 22.04.5 LTS
- Python 3.11.9
- Py-cord 2.6.1
- dotenv 1.1.0

# HOW TO USE
Discordのテキストチャンネル上で指定のコマンドを入力することで任意のコマンドが呼び出されます。

- /check
  - ロードされた関数とコマンドの一覧、OAuth2リンクが確認できます。
- /mng
  - get_members
    - サーバーメンバーのIDを鍵にポイント情報をメンバーと紐づけ、その情報をjsonとして保存します。
  - link
    - ロールとボイスチャンネルを紐づけし、その情報をjsonとして保存します。
  - set_ticket_channel
    - 問い合わせフォームカテゴリとアーカイブカテゴリを作成し、前者にチケット発行のためのチケットセンターという名前のテキストチャンネルを作成する。
- /point
  - check target(任意のメンバー。なくてもよい。)
    - targetのポイント残高を表示する。
  - plus target(任意のメンバー。入力必須) amount(ポイントの数)
    - targetにたいしてamount分のポイントを付与する。
  - minus target(任意のメンバー。入力必須) amount(ポイントの数)
    - taegetのポイントをamount分減らす。ただし、amountがtargetのポイントを上回る場合はこれをしない。

# OTHER INFORMATIONS
[OAuth2 リンク](https://discord.com/oauth2/authorize?client_id=1380828889156423761&permissions=8&integration_type=0&scope=bot+applications.commands)