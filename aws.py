import boto3


class ManipulateS3:
    def __init__(self , accesskey , secretkey , bucket_name , region = "ap-northeast-1"):
        self.region = region  # 東京(アジアパシフィック)：ap-northeast-1
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', aws_access_key_id=self.accesskey, aws_secret_access_key=self.secretkey, region_name=self.region)
    
    def get_file_name_from_file_path(self , file_path):
        """ パスからファイル名のみを抽出する関数
            s3にフォルダを作成し、ファイルをアップロードする場合は、この関数を使わずに、file_pathにフォルダ名を含める
        """
        file_name_from_path = file_path[file_path.rfind('/') + 1 : ]  # ファイルパスからファイル名のみを抽出
        return file_name_from_path
    
    def s3_file_upload(self , file_path):
        """ s3の特定のバケットにファイルをアップロードし、そのファイルのURLも取得する関数
            s3上のファイルが同一のファイル名であれば、s3内で上書き保存される
        """
        key_name = self.get_file_name_from_file_path(file_path)
        # s3へファイルをアップロード
        self.s3.upload_file(file_path, self.bucket_name, key_name)
        # S3へアップロードしたファイルへのURLを取得する
        s3_url = self.s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket_name, 'Key': key_name},
            ExpiresIn=3600,
            HttpMethod='GET'
        )
        return s3_url
    
    def s3_file_download(self , local_upload_path):
        """ s3の特定のバケットからファイル名で検索し、一致するファイルをダウンロードする関数
            local_file_pathのファイル名はs3で取得予定のファイル名を同一にする
        """
        key_name = self.get_file_name_from_file_path(local_upload_path)
        print(f"key_name : {key_name}")
        self.s3.download_file(self.bucket_name, key_name, local_upload_path)



