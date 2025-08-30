from flask import Flask, request, jsonify
import os, json, time, uuid, logging
import boto3
from botocore.exceptions import ClientError, ReadTimeoutError
from botocore.config import Config
#FLASK APP
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REGION = "us-east-1"  # Force US-EAST-1
SECRET_NAME = os.getenv("SECRET_NAME", "movies-series-agent-creds-v2")

boto_config = Config(
    read_timeout=300,
    connect_timeout=60,
    retries={'max_attempts': 5, 'mode': 'standard'}
)

sm = boto3.client("secretsmanager", region_name=REGION, config=boto_config)
agent_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=boto_config)
bedrock_agent = boto3.client("bedrock-agent", region_name=REGION, config=boto_config)

AGENT_ID = None
AGENT_ALIAS_ARN = None
AGENT_ALIAS_ID = None

def load_credentials():
    global AGENT_ID, AGENT_ALIAS_ARN, AGENT_ALIAS_ID
    resp = sm.get_secret_value(SecretId=SECRET_NAME)
    creds = json.loads(resp["SecretString"])
    AGENT_ID = creds["BEDROCK_AGENT_ID"].split("/")[-1]
    AGENT_ALIAS_ARN = creds["BEDROCK_AGENT_ALIAS_ARN"]
    AGENT_ALIAS_ID = AGENT_ALIAS_ARN.split("/")[-1]

def wait_for_alias(alias_arn, timeout=600, interval=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = bedrock_agent.get_agent_alias(AgentAliasArn=alias_arn)
            status = resp["AgentAlias"]["Status"]
            if status == "ACTIVE":
                return
        except Exception as e:
            print(f"Error checking alias status: {e}")
        time.sleep(interval)
    raise RuntimeError("Alias did not become ACTIVE in time")

load_credentials()
wait_for_alias(AGENT_ALIAS_ARN)

def invoke_with_retry(message, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            return agent_rt.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=str(uuid.uuid4()),
                inputText=message
            )
        except ReadTimeoutError:
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(2 ** attempt)

def parse_reply(response):
    parts = []
    for ev in response.get("completion", []):
        chunk = ev.get("chunk") or {}
        if "bytes" in chunk:
            parts.append(chunk["bytes"].decode())
        elif "text" in chunk:
            parts.append(chunk["text"])
    if not parts:
        raise RuntimeError("Empty completion from agent")
    return "".join(parts)

@app.route('/health', methods=['GET'])
def health():
    return jsonify(
        status="healthy" if AGENT_ID else "unhealthy",
        agent_id=AGENT_ID,
        alias_id=AGENT_ALIAS_ID
    )

@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify(error="JSON required"), 400
    body = request.get_json()
    msg = body.get("message")
    if not msg or not isinstance(msg, str) or not msg.strip():
        return jsonify(error="message must be a non-empty string"), 400
    if not AGENT_ID:
        return jsonify(error="Agent not configured"), 503
    try:
        raw = invoke_with_retry(msg)
        reply = parse_reply(raw)
        return jsonify(reply=reply)
    except ReadTimeoutError:
        return jsonify(error="Timeout invoking agent"), 504
    except ClientError as e:
        err = e.response.get("Error", {})
        return jsonify(error=err.get("Code", "ClientError") + ": " + err.get("Message", str(e))), 500
    except Exception as e:
        return jsonify(error=str(e)), 500
#startup
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091)
