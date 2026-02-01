import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("websocket-connection")

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]

    table.delete_item(
        Key={
            "connectionid": connection_id
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Disconnected")
    }