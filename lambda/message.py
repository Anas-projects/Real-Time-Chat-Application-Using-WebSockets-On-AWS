import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("websocket-connection")
messages_table = dynamodb.Table("chat-messages")

apigateway = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://ddmmyyyy.execute-api.us-east-1.amazonaws.com/production"
)

def lambda_handler(event, context):
    print("RAW EVENT:", json.dumps(event))


    if "body" in event and event["body"]:
        data = json.loads(event["body"])
    else:
        data = event  

    sender = data.get("sender", "unknown")
    message = data.get("message")

    if not message:
        print("No message found, skipping")
        return {"statusCode": 200}

    # Save message to DynamoDB
    messages_table.put_item(
        Item={
            "roomId": "global",
            "timestamp": datetime.utcnow().isoformat(),
            "sender": sender,
            "message": message
        }
    )

    # Broadcast to all connections
    connections = connections_table.scan().get("Items", [])
    print("Connections:", connections)

    for conn in connections:
        connection_id = conn["connectionid"]
        try:
            apigateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({
                    "sender": sender,
                    "message": message
                })
            )
        except Exception as e:
            print("Removing stale connection:", connection_id, str(e))
            connections_table.delete_item(
                Key={"connectionid": connection_id}
            )

    return {"statusCode": 200}