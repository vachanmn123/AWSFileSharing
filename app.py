import os
import shortuuid
import boto3
import watchtower
import logging
from flask import Flask, request, jsonify, redirect, render_template
import time

app = Flask(__name__)

S3_BUCKET_USER = "file-share-vachan"
DYNAMODB_TABLE_USER = "FileLinks"
AWS_ACCOUNT_ID = "841162670179"
AWS_REGION_USER = "ap-south-1"
SNS_TOPIC_USER = "FileUploadNotifications"

# AWS resource setup
S3_BUCKET = os.environ.get("S3_BUCKET", S3_BUCKET_USER)
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", DYNAMODB_TABLE_USER)

AWS_REGION = os.environ.get("AWS_REGION", AWS_REGION_USER)
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION

SNS_TOPIC_ARN = os.environ.get(
    "SNS_TOPIC_ARN",
    f"arn:aws:sns:{AWS_REGION}:{AWS_ACCOUNT_ID}:{SNS_TOPIC_USER}",
)

s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
sns = boto3.client("sns", region_name=AWS_REGION)

# CloudWatch logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(
    watchtower.CloudWatchLogHandler(
        log_group_name="FileShareLogs",
    )
)


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file_id = shortuuid.ShortUUID().random(length=7)
    s3_key = f"uploads/{file_id}-{file.filename}"
    s3.upload_fileobj(file, S3_BUCKET, s3_key)
    table.put_item(
        Item={
            "file_id": file_id,
            "s3_key": s3_key,
            "expire_at": int(time.time()) + 3600,
        }
    )
    link = f"{request.url_root}file/{file_id}"
    logger.info(f"File uploaded: {file.filename} as {s3_key} by {request.remote_addr}")
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="New File Uploaded",
        Message=f"File {file.filename} uploaded by {request.remote_addr}.",
    )
    return jsonify({"link": link})


@app.route("/file/<file_id>")
def get_file(file_id):
    response = table.get_item(Key={"file_id": file_id})
    item = response.get("Item")
    if not item:
        logger.warning(f"File not found: {file_id}")
        return "File not found", 404
    s3_key = item["s3_key"]
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key},
        ExpiresIn=3600,  # 1 hour
    )
    logger.info(f"File link accessed: {file_id} by {request.remote_addr}")
    return redirect(url)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
