import boto3
import random
import os
import json

s3 = boto3.client("s3")


def build_response(status_code, message, extra=None):
    """Build a standardized API response"""
    response_body = {"message": message} | (extra if extra else {})

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body),
    }


def get_line_from_file(bucket_name, file_key, line_number=None):
    """Get a specific line or random line from a file in S3"""
    try:
        # Get the file content from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response["Body"].read().decode("utf-8")

        # Split into lines and filter out empty lines
        lines = [line for line in file_content.split("\n") if line.strip()]

        if line_number is not None:
            # Convert to zero-based index and handle out of bounds
            index = int(line_number) - 1
            if 0 <= index < len(lines):
                return build_response(
                    200, "Line retrieved successfully", {"line": lines[index]}
                )
            else:
                return build_response(
                    400,
                    f"Line number {line_number} out of range. File has {len(lines)} lines.",
                )
        else:
            # Select a random line
            random_line = random.choice(lines)
            return build_response(
                200, "Random line retrieved successfully", {"line": random_line}
            )

    except Exception as e:
        return build_response(500, f"Error: {str(e)}")


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    bucket_name = os.environ["BUCKET_NAME"]
    file_key = os.environ["FILE_KEY"]

    line_number = event.get("queryStringParameters", {}).get("line_number")

    return get_line_from_file(bucket_name, file_key, line_number)
