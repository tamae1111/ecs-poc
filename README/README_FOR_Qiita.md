ECSで上げるまでのロジック
## まず最初にやること
このソース内の<<your_account_id>>を検索し、使用者のアカウントIDに置換する
このソース内の<<your_bucket_name>>を検索し、使用者のバケット名に置換する


## 手順1
codecommitでgitソースコードをアップ

## 手順2
まずgitは以下の以下テンプレートでvpcを作成する
vpc-01.yml

次にルート直下で以下コマンドを実行

例：
IMAGE_NAME=ml-ecs-poc
AWS_ACCOUNT=<<your_account_id>>

ECR_URL=<<your_account_id>>.dkr.ecr.ap-northeast-1.amazonaws.com/${IMAGE_NAME}:latest
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com

docker build -t ${IMAGE_NAME} .
docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com/${IMAGE_NAME}:latest
docker push ${AWS_ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com/${IMAGE_NAME}:latest

codebuild-ml-ecs-poc-build-service-role
というロールに以下の3つの権限をアタッチ
・ecrへのアクセス権限
・ssm:GetParameters
・AmazonSSMReadOnlyAccess


AWS Systems Manager-パラメータストアに以下を設定

名前 |	タイプ |	KMS | キーソース |	値 |h
/dockerhub/user |	安全な文字列 |	任意のキーを選択 |	DockerHub にログインするユーザ名 |
/dockerhub/pass |	安全な文字列 |	任意のキーを選択 |	DockerHub にログインするパスワード |

ECS

## 手順3
ここから、コンソールでパイプライン経由で、ECSクラスターとサービスの作成を行う

## 手順4
codepipelineにて、codecommitからcodebuild、ecsのビルド設定を行う。
参考：https://www.tdi.co.jp/miso/aws-codepipeline-amazon-ecsfargate

※codeBuildでプロジェクトの作成中にに以下環境変数を設定することを忘れない。
DOCKERHUB_USE |	/dockerhub/user	| パラメータ |
DOCKERHUB_PASS | /dockerhub/pass | パラメータ |

※詰まった時のヒント
imagedefinitions.jsonの中身が想定した通りか確認する
例：
[{"name":"<<container_name>>","imageUri":"<<your_account_id>>.dkr.ecr.ap-northeast-1.amazonaws.com/<<image_name>>:latest"}]


# 次、s3からデータをダウンロードするよう設定

## 手順1
ECS-Console-V2-Service-ml-ecs-poc-service-ml-ecs-poc-cluster-******のスタックを削除し、新たにもう一度追加

## 手順2
ecsTaskExecutionRoleという、タスク定義のタスク実行ロールに
・AmazonS3FullAccess
を設定（バケット制限をする方が望ましい）

そして、多分これは間違っているので、後でタスク実行ロールから
AmazonS3FullAccessを外して、
タスクロールにAmazonS3FullAccessを付与する

ecsTaskRoleを新たに作成し、(ecs-taskで実行を許可する形でロール作成)
・AmazonS3FullAccess
を設定

albをつけた形でecs-serviceを新たに作成する。
ここでlistenポートは8080
コンテナのポートマッピングも8080 to 8080としている。

ecs上でalbの設定を行う時は、以下ルールがあることに気を付ける。
同じアベイラビリティゾーンでは設定するサブネットは1つまで、
最低二つのアベイラビリティゾーンに紐づいたサブネットをつける必要がある

その後、s3にアクセスログのバケットを作り、アクセスログの確認を行う




