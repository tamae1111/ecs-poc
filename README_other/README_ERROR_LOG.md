# 発生したエラーとそれに対してやったこと

### 注：いずれエラーが出た時のために、軽く流し見てから他作業を行うのがおすすめ

## 発生したこと1：codeBuild実行時に権限エラーが発生（エラーメッセージは割愛）
AWSCodeBuildで使用されている　codebuild-ml-ecs-poc-build-service-role　というロールに
ecrへのアクセス権限をアタッチ

## 発生したこと2：コマンドエラーが発生
その際エラーが発生：COMMAND_EXECUTION_ERROR: Error while executing command docker build -t ***:latest .. Reason: exit status 

エラー原因：
結論としてはdockerファイルの置き場所と、ファイル名がDockerfileになってなかったのが原因だが、その判明に至るまでの試行をいかに記載する。
 
↓
### try1
$()を入れて実行してみた：↓
$(aws ecr get-login-password --region ap-northeast-1) | docker login --username AWS --password-stdin 
↓結果
だめだった：Command did not exit successfully $(aws ecr get-login-password --region ap-northeast-1) | docker login --username AWS --password-stdin 

$(aws ecr get-login-password --region ap-northeast-1　| docker login --username AWS --password-stdin ****.dkr.ecr.ap-northeast-1.amazonaws.com)
↓結果
ダメだった：Provided region_name 'ap-northeast-1' doesn't match a supported format.

### try2
iam:DeletePolicyVersionをつけてみた(以下を参考に　https://stackoverflow.com/questions/61893963/error-with-docker-build-stage-of-codebuild-build)

IAMManagePolicy
```
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": [
            "iam:DeletePolicyVersion",
            "ssm:GetParameters"
        ],
        "Resource": "*"
    }
}
```
↓結果
ダメだったPhase context status code: COMMAND_EXECUTION_ERROR Message: Error while executing command: docker push $REPOSITORY_URI:latest. Reason: exit status 1

### try3
プリビレッジモードをつけてもう一度試す。（Amazon-managed ubuntu imageを使用しつつ）
↓結果
ここが原因ではなかったが、プリビレッジモードは大事

### try4
echo ${DOCKERHUB_PASS} | docker login -u ${DOCKERHUB_USER} --password-stdin
を入れて試した

### try5
AmazonSSMReadOnlyAccessをつけた


### try6
エラータイミング：
code piplineでのcode build実行時

以下エラーが出た
unable to prepare context: unable to evaluate symlinks in Dockerfile path

↓対策
dockerfileの名前をDockerfileにして、ルート直下に配置した
そして、dockerfileの中でファイルのコピーを実行した

COPY ./dockerImage ./
COPY ./dockerImage/requirements.txt ./
COPY ./dockerImage/sample.py ./

↓結果
成功、buildまではできた


### try7
エラータイミング：
code piplineでのcodebuild時

出たエラー内容：
The Amazon ECS service 'ml-ecs-poc-service' is not active.
↓対策
ローカルでpython実行ファイルのコピー形式が間違っていたので修正した
↓結果
成功、buildまではできた

### try7-2
エラータイミング：
code piplineでのcodebuild時

出たエラー内容：
The Amazon ECS service 'ml-ecs-poc-service' is not active.

対策:
サービスが起動し続けるタイプのものではなかったので、python実行スクリプトをずっと起動するタイプに修正

結果：
成功


### try8
出たエラー内容：
code piplineでのecsデプロイのフェイズのところで以下エラーが出ていた
The image URI contains invalid characters.

対策:
buildspec.yml　内に　imagedefinitions.jsonに吐き出しているコマンドがあるのだが、その値がおかしかったので、
それを修正した

結果：
deployできた


### try 9
alb作成時、以下エラー発生：
A load balancer cannot be attached to multiple subnets in the same Availability Zone

対策：albの実態は一つのサブネットでターゲットグループが複数なのでとりあえず作り直すこととした

結果：以下エラーが出た、わがままalb(しゃーないけど)
At least two subnets in two different Availability Zones must be specified (Service: AmazonElasticLoadBalancing;

対策：
異なるアベイラビリティゾーンの一つずつのサブネットに紐付けた（合計二つのサブネットにくっつけた）

結果：
解決

### try 10
エラー内容：
ロードバランサーをつけようとしたらバグった Access Denied for bucket: <<your_bucket_name>>. Please check S3bucket permission
対策：
以下バケットポリシーを付与した(582318560864は自分のアカウントじゃないので注意)
{
    "Version": "2012-10-17",
    "Id": "PutObjPolicy",
    "Statement": [
        {
            "Sid": "DenyObjectsThatAreNotSSEKMS",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::582318560864:root"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::<<your_bucket_name>>/alb-access-log/*"
        }
    ]
}

### try 11
対策：
securityGroupのポートで8080が開放されていなかったので、開放した

結果：
全てうまくいった、albでもアクセスできるし、fargateのパブリックIPでも接続できる。素晴らしい。

### try 12
対策：
ただecsタスクに直接アクセスできるのは微妙なので、ALBもECS-TASKと同一のセキュリティグループに付属させることで、直接ECSタスクにアクセスできなくした
おそらくパブリック接続をなくす形でも達成可能だが、一旦この形とした

結果：
task直のアクセスは禁止し、ALB経由は可能となった


==========
### try template
エラー内容：

対策：

結果：